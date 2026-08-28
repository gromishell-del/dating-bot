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
    """Показ админ-панели"""
    if message.from_user.id not in ADMIN_IDS:
        await message.answer(" У тебя нет доступа к этой команде.")
        return
    
    await message.answer(
        "️ **Панель администратора**\n\n"
        "Выбери действие:",
        reply_markup=get_admin_keyboard(),
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "admin_users")
async def show_all_users(callback: CallbackQuery):
    """Показ всех пользователей"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    users = await get_all_users()
    
    if not users:
        await callback.message.edit_text("📭 Пользователей пока нет.")
        return
    
    text = "👥 **Все пользователи:**\n\n"
    
    # Показываем первых 20 пользователей
    for i, user in enumerate(users[:20], 1):
        # user: 0:user_id, 1:name, 2:age, 3:gender, 4:course, 5:faculty, 6:description, 7:photo_id, 8:is_active
        status = "✅" if user[8] else "🚫"
        gender = "М" if user[3] == "male" else "Ж"
        text += f"{i}. {status} **{user[1]}** ({user[2]} лет, {gender})\n"
        text += f"   ID: `{user[0]}` | Курс: {user[4]} | {user[5]}\n\n"
    
    if len(users) > 20:
        text += f"... и ещё {len(users) - 20} пользователей"
    
    await callback.message.edit_text(text, parse_mode="Markdown")

@router.callback_query(F.data == "admin_complaints")
async def show_all_complaints(callback: CallbackQuery):
    """Показ всех жалоб"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer(" Нет доступа", show_alert=True)
        return
    
    complaints = await get_all_complaints()
    
    if not complaints:
        await callback.message.edit_text("✅ Жалоб нет. Всё чисто!")
        return
    
    text = "️ **Жалобы:**\n\n"
    
    # Показываем последние 15 жалоб
    for i, comp in enumerate(complaints[:15], 1):
        # comp: 0:id, 1:from_user_id, 2:to_user_id, 3:reason, 4:created_at
        text += f"{i}. От: `{comp[1]}` → На: `{comp[2]}`\n"
        text += f"   Причина: {comp[3]}\n\n"
    
    await callback.message.edit_text(text, parse_mode="Markdown")

@router.message(Command("ban"))
async def ban_user_command(message: Message):
    """Команда для блокировки пользователя: /ban user_id"""
    if message.from_user.id not in ADMIN_IDS:
        return
    
    try:
        # Получаем ID из команды: /ban 123456789
        parts = message.text.split()
        if len(parts) < 2:
            await message.answer("Используй: /ban user_id\nНапример: /ban 123456789")
            return
        
        user_id_to_ban = int(parts[1])
        await ban_user(user_id_to_ban)
        
        await message.answer(f"✅ Пользователь `{user_id_to_ban}` заблокирован.", parse_mode="Markdown")
        
    except ValueError:
        await message.answer(" Ошибка: ID должен быть числом.")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")
