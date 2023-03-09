import asyncio
import telegram
import time
import re
from models import *
from config import url, TOKEN, reg, chat_id
from workers import (
    get_daily_summary, 
    check_workers, 
    compare_workers, 
    get_data_from_url, 
    engine, 
    get_workers_info, 
    get_workers_in_db
    )


async def send_msg(text):
    bot = telegram.Bot(TOKEN)
    async with bot:
        await bot.send_message(chat_id, text)


def create_msg_from_list(list_workers, text):
    for worker in list_workers:
        text = text + worker + '\n'
    return text


async def add_worker_info_in_db(engine):
    
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

        await asyncio.sleep(600)


async def send_current_info():
    
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
            text = 'Все асики работают!'
        else:
            text = create_msg_from_list(list_workers=inactive_workers, text='Не работают:\n')
        
        await send_msg(text)
        await asyncio.sleep(3600)


async def send_fallen_workers():
    current_active_workers = []
    while True:
        if current_active_workers == []:
            print('Enter without workers')
            current_active_workers = check_workers(url)
            await asyncio.sleep(10)
            continue
        else:
            print('Enter with workers')
            previous_active_workers = current_active_workers
            current_active_workers = check_workers(url)
            fallen_workers = compare_workers(previous_active_workers, current_active_workers)
            
            text = create_msg_from_list(list_workers=fallen_workers, text='Упали:\n')
            await send_msg(text)
            await asyncio.sleep(10)


async def send_daily_summary():

    while True:
        text = get_daily_summary()
        await send_msg(text)
        await asyncio.sleep(86400)


async def main():
    task1 = asyncio.create_task(send_current_info())
    task2 = asyncio.create_task(send_fallen_workers())
    task3 = asyncio.create_task(send_daily_summary())
    task4 = asyncio.create_task(add_worker_info_in_db(engine))
    await asyncio.gather(task1, task2, task3, task4)


if __name__ == '__main__':
    asyncio.run(main())