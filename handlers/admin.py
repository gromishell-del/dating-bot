# handlers/admin.py
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command
from database import get_all_users, get_all_complaints, ban_user
from keyboards import get_admin_keyboard
from config import ADMIN_IDS

router = Router()

@router.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    await message.answer("⚙️ Панель администратора:", reply_markup=get_admin_keyboard())

@router.callback_query(F.data == "admin_users")
async def show_users(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS: return
    users = await get_all_users()
    text = "👥 Пользователи:\n" + "\n".join([f"ID: {u[0]}, {u[1]}, {u[2]} лет (Активен: {u[8]})" for u in users[:15]])
    await callback.message.edit_text(text)

@router.callback_query(F.data == "admin_complaints")
async def show_comps(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS: return
    comps = await get_all_complaints()
    if not comps:
        await callback.message.edit_text("Жалоб нет ✅")
        return
    text = "⚠️ Жалобы:\n" + "\n".join([f"От {c[0]} на {c[1]}: {c[2]}" for c in comps])
    await callback.message.edit_text(text)

@router.message(F.text.startswith("ban "))
async def ban_cmd(message: Message):
    if message.from_user.id not in ADMIN_IDS: return
    try:
        user_id = int(message.text.split()[1])
        await ban_user(user_id)
        await message.answer(f"✅ Пользователь {user_id} заблокирован.")
    except:
        await message.answer("Используй: ban [ID_пользователя]")