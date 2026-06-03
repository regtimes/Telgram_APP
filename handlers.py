from aiogram import Router, F, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import database as db_methods

router = Router()

def get_start_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🏢 Офис")]],
        resize_keyboard=True
    )

def get_register_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Поделиться номером телефона", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

@router.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        "Для авторизации нажмите офис",
        reply_markup=get_start_keyboard()
    )

@router.message(F.text == "🏢 Офис")
async def handle_office(message: types.Message):
    user_id = message.from_user.id
    phone = await db_methods.get_user_phone(user_id)

    if phone:
        await message.answer(
            f"🔓 Вы вошли в Личный Кабинет.\nВаш номер телефона: {phone}",
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        await message.answer(
            "Для входа в личный кабинет необходимо пройти авторизацию.",
            reply_markup=get_register_keyboard()
        )

@router.message(F.contact)
async def handle_contact(message: types.Message):
    if message.contact.user_id != message.from_user.id:
        await message.answer("Пожалуйста, отправьте именно свой контакт.")
        return

    user_id = message.from_user.id
    await db_methods.save_user(
        user_id=user_id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        phone=message.contact.phone_number
    )

    await message.answer(
        "🎉 Авторизация успешно завершена! Личный кабинет открыт.",
        reply_markup=ReplyKeyboardRemove()
    )
