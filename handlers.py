from aiogram import Router, F, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import database as db_methods

router = Router()


@router.message(CommandStart())
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    phone = await db_methods.get_user_phone(user_id)

    if phone:
        await message.answer(f"Привет, {message.from_user.first_name}! Вы уже зарегистрированы. Ваш номер: {phone}")
    else:
        kb = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="📱 Поделиться номером телефона", request_contact=True)]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await message.answer(
            f"Для работы с ботом необходимо пройти регистрацию.",
            reply_markup=kb
        )


@router.message(F.contact)
async def handle_contact(message: types.Message):
    if message.contact.user_id != message.from_user.id:
        await message.answer("Пожалуйста, отправьте именно свой контакт с помощью кнопки ниже.")
        return

    user_id = message.from_user.id
    await db_methods.save_user(
        user_id=user_id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        phone=message.contact.phone_number
    )

    await message.answer(
        f"Регистрация успешна. Ваш номер {message.contact.phone_number}.",
        reply_markup=ReplyKeyboardRemove()
    )
