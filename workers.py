import requests
import re
from datetime import datetime, timedelta
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from models import *
from config import url, reg


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


def get_daily_summary():
    data = get_data_from_url(url)

    past_24h_rewards = data['user']['past_24h_rewards']
    ltc_rub = data['market']['ltc_rub']
    past_24h_reward_in_rub = round(past_24h_rewards * ltc_rub, 2)

    yesteday = datetime.now().date() - timedelta(days=1)

    connection = engine.connect()
    session = Session(connection)
    stmt = select(WorkerInfo).where(WorkerInfo.time.contains(yesteday))
    workers = session.scalars(stmt).all()
    total_hash_rate = 0
    counter = 0
    for worker in workers:
        total_hash_rate += worker.hash_rate
        counter += 1
    
    session.close()
    average_hash_rate = total_hash_rate / counter

    date = f'Сводка за {yesteday}:\n'
    average_speed = f'Средний хешрейт асиков: {round(average_hash_rate, 2)}\n'
    rubles = f'Заработано: {past_24h_reward_in_rub} рублей\n'
    text = date + average_speed + rubles

    return text