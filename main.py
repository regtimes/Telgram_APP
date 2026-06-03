import asyncio
import os
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from database import init_db
from handlers import router

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")


async def main():
    await init_db()
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    print("Бот успешно запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот успешно остановлен пользователем.")
