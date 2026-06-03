from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# 1. Стартовое меню — только одна кнопка
def get_start_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🏢 Офис")]],
        resize_keyboard=True
    )

# 2. Меню регистрации
def get_register_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Поделиться номером телефона", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

# 3. Меню Личного Кабинета после авторизации
def get_profile_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="⬅️ Выйти в главное меню")]],
        resize_keyboard=True
    )
