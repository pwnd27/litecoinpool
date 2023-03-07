import time
import requests
import re
from datetime import datetime
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from models import *


def get_data_from_url(url):
    response = requests.get(url)
    data = response.json()
    return data


def get_workers_info(url):

    reg = r'\w{6}.\d{3}\w\d{2}'
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


def add_info_in_db(engine, workers, worker_info):
    
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


def check_workers(url):

    reg = r'\w{6}.\d{3}\w\d{2}'
    data = get_data_from_url(url)

    active_workers = []

    for worker in data.get('workers'):
        match = re.fullmatch(reg, worker)
        if match:
            hash_rate = data['workers'][worker]['hash_rate']
            if hash_rate != 0:
                active_workers.append(worker)


    print(f'> active workers: {active_workers}')
    return active_workers


def compare_workers(previous_workers, current_workers):
    
    fallen_workers = []
    if previous_workers == current_workers:
        return fallen_workers
    
    for worker in previous_workers:
        if worker not in current_workers:
            fallen_workers.append(worker)
    
    return fallen_workers




def get_info():
    
    url = 'https://www.litecoinpool.org/api?api_key=509bcec844b156d6b806953ce89e6c27'
    engine = create_engine('sqlite:///litecoin.db', echo=True)
    
    workers = get_workers_in_db(engine)

    worker_info = get_workers_info(url)

    # add_info_in_db(engine, workers, worker_info)
    
    return worker_info



def get_fallen_workers():
    current_active_workers = []
    while True:
        if current_active_workers == []:
            current_active_workers = check_workers('https://www.litecoinpool.org/api?api_key=509bcec844b156d6b806953ce89e6c27')
            time.sleep(10)
            continue
        else:
            previous_active_workers = current_active_workers
            current_active_workers = check_workers('https://www.litecoinpool.org/api?api_key=509bcec844b156d6b806953ce89e6c27')
            fallen_workers = compare_workers(previous_active_workers, current_active_workers)
            print(f'> fallen workers: {fallen_workers}')
            time.sleep(10)