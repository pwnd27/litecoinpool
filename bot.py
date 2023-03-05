import asyncio
import telegram


async def main():
    bot = telegram.Bot("2146793930:AAGZfmhgBvJMbni2kuCA6QAh1eeFXkAEAS4")
    async with bot:
        print((await bot.get_updates()))


if __name__ == '__main__':
    asyncio.run(main())