import time
import requests
import re
from datetime import datetime, timedelta
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from models import *
from config import url, reg, eng


engine = create_engine('sqlite:///litecoin.db', echo=True)

def get_data_from_url(url):
    response = requests.get(url)
    data = response.json()
    return data


def get_workers_info(url):

    data = get_data_from_url(url)

    worker_info = {}
    current_time = datetime.utcnow()

    for worker in data.get('workers'):
        match = re.fullmatch(reg, worker)
        if match:
            connected = data['workers'][worker]['connected']
            hash_rate = data['workers'][worker]['hash_rate']
            worker_info.update({worker: [hash_rate, connected, current_time]})
    
    return worker_info


def get_workers_in_db(engine):

    connection = engine.connect()
    session = Session(connection)
    workers = session.scalars(select(Worker)).all()
    session.close()

    return workers


def check_workers(url):

    data = get_data_from_url(url)

    active_workers = []

    for worker in data.get('workers'):
        match = re.fullmatch(reg, worker)
        if match:
            hash_rate = data['workers'][worker]['hash_rate']
            if hash_rate != 0:
                active_workers.append(worker)


    return active_workers


def compare_workers(previous_workers, current_workers):
    
    fallen_workers = []
    if previous_workers == current_workers:
        return fallen_workers
    
    for worker in previous_workers:
        if worker not in current_workers:
            fallen_workers.append(worker)
    
    return fallen_workers


def add_worker_info_in_db(engine):
    
    workers = get_workers_in_db(engine)
    
    while True:
        worker_info = get_workers_info(url)
        to_add = []

        for worker, info in worker_info.items():
            for worker_in_db in workers:
                if worker == worker_in_db.name:
                    worker_id = worker_in_db.id
            obj = WorkerInfo(
                worker_id=worker_id,
                hash_rate=info[0],
                connected=info[1],
                time=info[2],
            )
            to_add.append(obj)

        with Session(engine) as session:
            session.add_all(to_add)
            session.commit()

        time.sleep(600)


def get_current_info(url):    
    while True: 
        data = get_data_from_url(url)

        inactive_workers = []

        for worker in data.get('workers'):
            match = re.fullmatch(reg, worker)
            if match:
                hash_rate = data['workers'][worker]['hash_rate']
                if hash_rate == 0:
                    inactive_workers.append(worker)

        if inactive_workers == []:
            print(f'Все асики работают!')
        else:
            print(f'Не работают: {inactive_workers}')
        
        time.sleep(3600)


def get_fallen_workers():
    current_active_workers = []
    while True:
        if current_active_workers == []:
            print('Enter without workers')
            current_active_workers = check_workers(url)
            time.sleep(10)
            continue
        else:
            print('Enter with workers')
            previous_active_workers = current_active_workers
            current_active_workers = check_workers(url)
            fallen_workers = compare_workers(previous_active_workers, current_active_workers)
            yield f'Упали: {fallen_workers}'
            time.sleep(10)


def get_daily_summary():
    data = get_data_from_url(url)

    past_24h_rewards = data['user']['past_24h_rewards']
    ltc_rub = data['market']['ltc_rub']
    past_24h_reward_in_rub = round(past_24h_rewards * ltc_rub, 2)

    yestoday = datetime.now().date() - timedelta(days=1)

    connection = engine.connect()
    session = Session(connection)
    stmt = select(WorkerInfo).where(WorkerInfo.time.contains(yestoday))
    workers = session.scalars(stmt).all()
    total_hash_rate = 0
    workers_count = 0
    for worker in workers:
        total_hash_rate += worker.hash_rate
        workers_count += 1
    
    session.close()
    average_hash_rate = total_hash_rate / workers_count

    date = f'Сводка за {yestoday}:\n'
    average_speed = f'Средний хешрейт асиков: {round(average_hash_rate, 2)}\n'
    rubles = f'Заработано: {past_24h_reward_in_rub} рублей\n'
    text = date + average_speed + rubles

    return text