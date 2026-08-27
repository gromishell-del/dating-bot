# handlers/complaints.py
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import add_complaint

router = Router()

class CompState(StatesGroup):
    reason = State()

@router.callback_query(F.data.startswith("comp_reason_"))
async def process_complaint(callback: CallbackQuery, state: FSMContext):
    # data выглядит как comp_reason_12345_spam
    parts = callback.data.split("_")
    to_id = int(parts[2])
    reason = parts[3]
    
    await add_complaint(callback.from_user.id, to_id, reason)
    await callback.message.edit_text("⚠️ Жалоба отправлена администратору. Спасибо за бдительность!")
    await state.clear()