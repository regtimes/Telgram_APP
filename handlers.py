from aiogram import Router, F, types
from aiogram.filters import CommandStart
import database as db_methods
import keyboards as kb

router = Router()


@router.message(CommandStart())
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    phone = await db_methods.get_user_phone(user_id)
    role = await db_methods.get_user_role(user_id)
    is_admin_user = (role == "Administrator")

    if phone:
        # Оставляем одно аккуратное текстовое сообщение, чтобы кнопки жестко зафиксировались на экране
        await message.answer(
            "📋 Главное меню",
            reply_markup=kb.get_start_keyboard(is_admin=is_admin_user)
        )
    else:
        # Для незарегистрированных пользователей всё остается по-прежнему
        await message.answer(
            "Нажмите кнопку ниже для регистрации в системе:",
            reply_markup=kb.get_register_keyboard()
        )



@router.message(F.text == "🏢 Офис")
async def handle_office(message: types.Message):
    user_id = message.from_user.id
    phone = await db_methods.get_user_phone(user_id)
    role = await db_methods.get_user_role(user_id)

    try:
        await message.delete()
    except Exception:
        pass

    if phone:
        if role == "User":
            await message.answer("⏳ Доступ ограничен. Ожидайте подтверждения доступа от администратора...")
            return

        await message.answer(
            "📱 [Заглушка WebApp приложения]\n\n"
            "Приложение Склада успешно открыто.\n"
            "Для выхода нажмите кнопку ниже ⬇️",
            reply_markup=kb.get_app_close_keyboard()
        )
    else:
        await message.answer(
            "Нажмите кнопку ниже для регистрации в системе:",
            reply_markup=kb.get_register_keyboard()
        )


@router.message(F.contact)
async def handle_contact(message: types.Message):
    if message.contact.user_id != message.from_user.id:
        await message.answer("Пожалуйста, отправьте именно свой контакт.")
        return

    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name

    # Очищаем номер от лишних знаков (плюсов), если они прилетели от Telegram
    phone = message.contact.phone_number.replace("+", "")

    # Сохраняем пользователя в БД
    await db_methods.save_user(
        user_id=user_id,
        username=username,
        first_name=first_name,
        phone=phone
    )

    # ИСПРАВЛЕНО: Проверка на конкретный номер телефона для авто-выдачи прав админа
    if phone == "380933050011":
        await db_methods.update_user_role(user_id, "Administrator")
        is_admin_user = True
        success_text = "🎉 Вы успешно зарегистрированы в системе как **Администратор**!"
    else:
        is_admin_user = False
        success_text = "⏳ Регистрация завершена. Ожидайте подтверждения доступа от администратора..."

    try:
        await message.delete()
        await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    except Exception:
        pass

    await message.answer(
        success_text,
        reply_markup=kb.get_start_keyboard(is_admin=is_admin_user),
        parse_mode="Markdown" if is_admin_user else None
    )

    # Если зарегистрировался ОБЫЧНЫЙ пользователь — отправляем уведомление админам
    if phone != "380933050011":
        all_users = await db_methods.get_all_users()
        admin_ids = [u.user_id for u in all_users if u.role == "Administrator"]

        admin_text = (
            f"👤 **Новый запрос на авторизацию!**\n\n"
            f"• ID: `{user_id}`\n"
            f"• Имя: {first_name}\n"
            f"• Ник: @{username if username else 'нет'}\n"
            f"• Тел: {phone}\n\n"
            f"Выберите роль для предоставления доступа:"
        )

        for admin_id in admin_ids:
            try:
                await message.bot.send_message(
                    chat_id=admin_id,
                    text=admin_text,
                    parse_mode="Markdown",
                    reply_markup=kb.get_admin_approve_keyboard(user_id)
                )
            except Exception:
                pass


@router.message(F.text == "📩 Отправить")
async def handle_send_click(message: types.Message):
    user_id = message.from_user.id
    phone = await db_methods.get_user_phone(user_id)

    try:
        await message.delete()
    except Exception:
        pass

    if phone:
        await message.answer("В данный момент нет активных посылок для отправки.")
    else:
        await message.answer("Сначала необходимо пройти авторизацию.")


@router.callback_query(F.data == "close_app_window")
async def handle_close_app(callback: types.CallbackQuery):
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.answer()


@router.message(F.text == "ℹ️ Инфо по штрихкоду")
async def handle_barcode_info(message: types.Message):
    user_id = message.from_user.id
    role = await db_methods.get_user_role(user_id)

    try:
        await message.delete()
    except Exception:
        pass

    if role != "Administrator":
        return

    await message.answer(
        "🤖 **Инфо по штрихкоду (Техническая панель):**\n\n"
        "• Форматы сканирования: EAN-13, QR-код, Code 128\n"
        "• Статус интеграции: Ожидание подключения камеры WebApp\n"
        "• Режим разбора: Автоматический парсинг накладных",
        parse_mode="Markdown"
    )
