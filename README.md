# Telgram_APP

Коммерческий Telegram-бот для управления посылками и автоматического уведомления получателей. Написан на Python с использованием асинхронной библиотеки `aiogram 3` и ORM `SQLAlchemy`.

## 🛠 Технологии
* **Python 3.11+**
* **Aiogram 3.x** (Асинхронный фреймворк для Telegram ботов)
* **SQLAlchemy 2.x** (ORM для работы с базой данных)
* **SQLite / PostgreSQL** (База данных)

## 🚀 Быстрый старт

### 1. Настройка окружения
```bash
python -m venv .venv
.venv\Scripts\activate     # Для Windows
pip install -r requirements.txt
```

### 2. Настройка переменных окружения
Создайте файл `.env` в корневой директории и добавьте туда ваш токен:
```env
BOT_TOKEN=ваш_токен_от_botfather
DATABASE_URL=sqlite+aiosqlite:///warehouse_bot.db
```

### 3. Запуск бота
```bash
python main.py
```
