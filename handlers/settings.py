# handlers/settings.py
from aiogram import Router, F
from aiogram.types import Message
from keyboards import get_main_keyboard

router = Router()

@router.message(F.text.contains("Настройки"))
async def show_settings(message: Message):
    """Показать настройки"""
    await message.answer(
        "️ **Настройки**\n\n"
        "Здесь скоро будут:\n"
        "• Редактирование анкеты\n"
        "• Фильтры поиска\n"
        "• Уведомления\n\n"
        "Функция в разработке! 🔧",
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )
