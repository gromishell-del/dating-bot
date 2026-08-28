# keyboards.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_main_keyboard():
    """Главная клавиатура"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👤 Моя анкета"), KeyboardButton(text=" Поиск пары")],
            [KeyboardButton(text="⚙️ Настройки")]
        ],
        resize_keyboard=True
    )

def get_gender_keyboard():
    """Выбор пола"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Парень", callback_data="gender_male")],
        [InlineKeyboardButton(text="Девушка", callback_data="gender_female")]
    ])

def get_course_keyboard():
    """Выбор курса"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1", callback_data="course_1"), 
         InlineKeyboardButton(text="2", callback_data="course_2")],
        [InlineKeyboardButton(text="3", callback_data="course_3"), 
         InlineKeyboardButton(text="4", callback_data="course_4")],
        [InlineKeyboardButton(text="5", callback_data="course_5"), 
         InlineKeyboardButton(text="Магистр", callback_data="course_6")]
    ])

def get_action_keyboard(user_id):
    """Кнопки действий с анкетой"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❤️ Нравится", callback_data=f"like_{user_id}")],
        [InlineKeyboardButton(text="❌ Пропустить", callback_data=f"skip_{user_id}")],
        [InlineKeyboardButton(text="⚠️ Пожаловаться", callback_data=f"complaint_{user_id}")]
    ])

def get_complaint_reasons(user_id):
    """Причины жалобы"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Спам", callback_data=f"comp_reason_{user_id}_spam")],
        [InlineKeyboardButton(text="Оскорбления", callback_data=f"comp_reason_{user_id}_insult")],
        [InlineKeyboardButton(text="Неадекватное фото", callback_data=f"comp_reason_{user_id}_photo")]
    ])

def get_admin_keyboard():
    """Админ-панель"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👥 Пользователи", callback_data="admin_users")],
        [InlineKeyboardButton(text="⚠️ Жалобы", callback_data="admin_complaints")]
    ])
