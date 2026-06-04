from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_start_keyboard(is_admin: bool = False) -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text="🏢 Офис")],
        [KeyboardButton(text="📩 Отправить")]
    ]
    if is_admin:
        buttons.insert(1, [KeyboardButton(text="ℹ️ Инфо по штрихкоду")])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_register_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Поделиться номером телефона", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def get_app_close_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Закрыть приложение", callback_data="close_app_window")]
    ])

def get_admin_approve_keyboard(target_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🛡️ Админ", callback_data=f"fastrole_{target_id}_Administrator"),
            InlineKeyboardButton(text="👥 Куратор", callback_data=f"fastrole_{target_id}_Curator")
        ],
        [
            InlineKeyboardButton(text="📟 Оператор", callback_data=f"fastrole_{target_id}_Operator"),
            InlineKeyboardButton(text="🚫 Отклонить", callback_data=f"fastrole_{target_id}_User")
        ]
    ])
