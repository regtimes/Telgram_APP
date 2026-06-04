from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import database as db_methods
import keyboards as kb

admin_router = Router()


class RoleChangeState(StatesGroup):
    wait_for_user_id = State()


async def is_admin(user_id: int) -> bool:
    role = await db_methods.get_user_role(user_id)
    return role == "Administrator"


@admin_router.message(Command("admin"))
async def admin_panel(message: types.Message):
    if not await is_admin(message.from_user.id):
        return

    try:
        await message.delete()
    except Exception:
        pass

    users = await db_methods.get_all_users()
    if not users:
        await message.answer("В базе данных еще нет пользователей.")
        return

    text = "👥 **Список зарегистрированных пользователей:**\n\n"
    for u in users:
        text += f"ID: `{u.user_id}` | Имя: {u.first_name} | Роль: *{u.role}*\n📱 Тел: {u.phone_number}\n\n"

    kb_inline = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚙️ Изменить права доступа", callback_data="change_role_start")]
    ])

    await message.answer(text, parse_mode="Markdown", reply_markup=kb_inline)


@admin_router.callback_query(F.data == "change_role_start")
async def change_role_start(callback: types.CallbackQuery, state: FSMContext):
    if not await is_admin(callback.from_user.id):
        await callback.answer("У вас нет прав.")
        return

    try:
        await callback.message.delete()
    except Exception:
        pass

    await callback.message.answer("Введите Telegram ID пользователя, которому хотите изменить права:")
    await state.set_state(RoleChangeState.wait_for_user_id)
    await callback.answer()


@admin_router.message(RoleChangeState.wait_for_user_id)
async def process_user_id(message: types.Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        return

    try:
        target_id = int(message.text)
        await message.delete()
    except ValueError:
        await message.answer("ID должен состоять только из цифр. Попробуйте еще раз:")
        return

    await state.clear()

    kb_inline = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Администратор", callback_data=f"setrole_{target_id}_Administrator"),
            InlineKeyboardButton(text="Куратор", callback_data=f"setrole_{target_id}_Curator")
        ],
        [
            InlineKeyboardButton(text="Оператор", callback_data=f"setrole_{target_id}_Operator"),
            InlineKeyboardButton(text="Пользователь", callback_data=f"setrole_{target_id}_User")
        ]
    ])

    await message.answer(f"Выберите новую роль для пользователя `{target_id}`:", parse_mode="Markdown",
                         reply_markup=kb_inline)


# Исправлено: Добавлено автоматическое уведомление пользователя при ручной смене роли через /admin
@admin_router.callback_query(F.data.startswith("setrole_"))
async def process_set_role(callback: types.CallbackQuery):
    if not await is_admin(callback.from_user.id):
        await callback.answer("У вас нет прав.")
        return

    try:
        await callback.message.delete()
    except Exception:
        pass

    data = callback.data.split("_")
    target_id = int(data[1])
    new_role = data[2]

    success = await db_methods.update_user_role(target_id, new_role)

    if success:
        await callback.message.answer(f"✅ Роль пользователя `{target_id}` успешно изменена на *{new_role}*.",
                                      parse_mode="Markdown")

        # Добавлен пропущенный блок уведомления пользователя в чат
        try:
            is_target_admin = (new_role == "Administrator")
            if new_role != "User":
                user_text = f"🎉 Вам изменены права доступа! Новая роль: **{new_role}**.\nТеперь вы можете открыть «🏢 Офис»."
            else:
                user_text = "❌ Ваши права доступа в личный кабинет были отозваны администратором."

            await callback.bot.send_message(
                chat_id=target_id,
                text=user_text,
                parse_mode="Markdown",
                reply_markup=kb.get_start_keyboard(is_admin=is_target_admin)
            )
        except Exception:
            pass
    else:
        await callback.message.answer("❌ Пользователь с таким ID не найден в базе данных.")

    await callback.answer()


@admin_router.callback_query(F.data.startswith("fastrole_"))
async def process_fast_role(callback: types.CallbackQuery):
    if not await is_admin(callback.from_user.id):
        await callback.answer("У вас нет прав.", show_alert=True)
        return

    data = callback.data.split("_")
    target_id = int(data[1])
    new_role = data[2]

    success = await db_methods.update_user_role(target_id, new_role)

    if success:
        try:
            await callback.message.delete()
        except Exception:
            pass

        try:
            is_target_admin = (new_role == "Administrator")
            if new_role != "User":
                user_text = f"🎉 Вам предоставлен доступ: **{new_role}**.\nТеперь вы можете открыть «🏢 Офис»."
            else:
                user_text = "❌ Ваш запрос на доступ в личный кабинет был отклонен администратором."

            await callback.bot.send_message(
                chat_id=target_id,
                text=user_text,
                parse_mode="Markdown",
                reply_markup=kb.get_start_keyboard(is_admin=is_target_admin)
            )
        except Exception:
            pass
    else:
        await callback.message.answer("❌ Ошибка: Пользователь не найден в базе данных.")

    await callback.answer()
