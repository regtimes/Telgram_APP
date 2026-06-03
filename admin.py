from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import database as db_methods

admin_router = Router()


# Состояния для смены роли (FSM)
class RoleChangeState(StatesGroup):
    wait_for_user_id = State()


# Проверка: является ли пользователь Администратором
async def is_admin(user_id: int) -> bool:
    role = await db_methods.get_user_role(user_id)
    return role == "Administrator"


# Команда /admin — показывает список пользователей
@admin_router.message(Command("admin"))
async def admin_panel(message: types.Message):
    if not await is_admin(message.from_user.id):
        return

    users = await db_methods.get_all_users()
    if not users:
        await message.answer("В базе данных еще нет пользователей.")
        return

    text = "👥 **Список зарегистрированных пользователей:**\n\n"
    for u in users:
        text += f"ID: `{u.user_id}` | Имя: {u.first_name} | Роль: *{u.role}*\n📱 Тел: {u.phone_number}\n\n"

    # Кнопка для назначения прав доступа
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚙️ Изменить права доступа", callback_data="change_role_start")]
    ])

    await message.answer(text, parse_mode="Markdown", reply_markup=kb)


# Начало процесса смены роли
@admin_router.callback_query(F.data == "change_role_start")
async def change_role_start(callback: types.CallbackQuery, state: FSMContext):
    if not await is_admin(callback.from_user.id):
        await callback.answer("У вас нет прав.")
        return

    await callback.message.answer("Введите Telegram ID пользователя, которому хотите изменить права:")
    await state.set_state(RoleChangeState.wait_for_user_id)
    await callback.answer()


# Получаем ID и выводим кнопки выбора новой роли
@admin_router.message(RoleChangeState.wait_for_user_id)
async def process_user_id(message: types.Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        return

    try:
        target_id = int(message.text)
    except ValueError:
        await message.answer("ID должен состоять только из цифр. Попробуйте еще раз:")
        return

    await state.clear()

    # Создаем инлайн-кнопки для выбора ролей
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Администратор", callback_data=f"setrole_{target_id}_Administrator"),
            InlineKeyboardButton(text="Куратор", callback_data=f"setrole_{target_id}_Curator")
        ],
        [
            InlineKeyboardButton(text="Оператор", callback_data=f"setrole_{target_id}_Operator"),
            InlineKeyboardButton(text="Пользователь", callback_data=f"setrole_{target_id}_User")
        ]
    ])

    await message.answer(f"Выберите новую роль для пользователя `{target_id}`:", parse_mode="Markdown", reply_markup=kb)


# Обработка нажатия на кнопку выбора роли
@admin_router.callback_query(F.data.startswith("setrole_"))
async def process_set_role(callback: types.CallbackQuery):
    if not await is_admin(callback.from_user.id):
        await callback.answer("У вас нет прав.")
        return

    # Разбираем callback_data (setrole_ID_РОЛЬ)
    data = callback.data.split("_")
    target_id = int(data[1])
    new_role = data[2]

    success = await db_methods.update_user_role(target_id, new_role)

    if success:
        await callback.message.answer(f"✅ Роль пользователя `{target_id}` успешно изменена на *{new_role}*.",
                                      parse_mode="Markdown")
    else:
        await callback.message.answer("❌ Пользователь с таким ID не найден в базе данных.")

    await callback.answer()
