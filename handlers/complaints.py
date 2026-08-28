# handlers/complaints.py
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from database import add_complaint

router = Router()

@router.callback_query(F.data.startswith("comp_reason_"))
async def process_complaint_reason(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора причины жалобы"""
    # Данные выглядят как: comp_reason_12345_spam
    parts = callback.data.split("_")
    
    if len(parts) < 4:
        await callback.answer("❌ Ошибка. Попробуй ещё раз.", show_alert=True)
        return
    
    to_user_id = int(parts[2])
    reason_code = parts[3]
    
    # Расшифровываем причину
    reasons = {
        "spam": "Спам/реклама",
        "insult": "Оскорбления/неадекватное поведение",
        "photo": "Неподходящее фото"
    }
    
    reason_text = reasons.get(reason_code, "Другая причина")
    
    # Добавляем жалобу в базу
    await add_complaint(callback.from_user.id, to_user_id, reason_text)
    
    await callback.message.edit_text(
        "✅ **Жалоба отправлена!**\n\n"
        f"Причина: {reason_text}\n\n"
        "Администратор рассмотрит её в ближайшее время.\n"
        "Спасибо за помощь в поддержании порядка! 👍",
        parse_mode="Markdown"
    )
    
    await state.clear()
