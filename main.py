import asyncio
import telegram
import time
from workers import get_info


async def main():
    chat_id = -469403074
    my_chat_id = 1098949498
    while True:
        text = 'Не работают:\n\n'
        send = False
        workers = get_info()
        for name, param in workers.items():
            if param[0] == 0:
                send = True
                text = text + name + '\n'

        if send:
            bot = telegram.Bot("2146793930:AAGZfmhgBvJMbni2kuCA6QAh1eeFXkAEAS4")
            async with bot:
                await bot.send_message(my_chat_id, text)

        time.sleep(600)

if __name__ == '__main__':
    asyncio.run(main())