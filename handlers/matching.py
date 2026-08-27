# handlers/matching.py
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from database import get_user, get_random_profile, add_like, check_mutual_like
from keyboards import get_action_keyboard
from config import BOT_TOKEN

router = Router()
bot = Bot(token=BOT_TOKEN)

@router.message(F.text == "🔍 Поиск пары")
async def start_search(message: Message):
    if not await get_user(message.from_user.id):
        await message.answer("Сначала зарегистрируйся через /start")
        return
    await show_profile(message.from_user.id, message)

async def show_profile(current_user_id, target):
    profile = await get_random_profile(current_user_id)
    if not profile:
        text = "Пока нет других анкет 😔 Загляни позже!"
        if hasattr(target, 'edit_text'):
            await target.edit_text(text)
        else:
            await target.answer(text)
        return

    # profile: 0-id, 1-name, 2-age, 3-gender, 4-course, 5-faculty, 6-desc, 7-photo
    gender_ru = "Парень" if profile[3] == "male" else "Девушка"
    text = f"👤 **{profile[1]}**, {profile[2]} лет\n🎓 {profile[4]} курс, {profile[5]}\n💬 {profile[6]}"
    
    kb = get_action_keyboard(profile[0])
    
    if hasattr(target, 'edit_text'): # Если это нажатие кнопки
        if profile[7]:
            await target.message.answer_photo(profile[7], caption=text, reply_markup=kb, parse_mode="Markdown")
            await target.message.delete()
        else:
            await target.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    else: # Если это обычное сообщение
        if profile[7]:
            await target.answer_photo(profile[7], caption=text, reply_markup=kb, parse_mode="Markdown")
        else:
            await target.answer(text, reply_markup=kb, parse_mode="Markdown")

@router.callback_query(F.data.startswith("like_"))
async def process_like(callback: CallbackQuery):
    to_id = int(callback.data.split("_")[1])
    from_id = callback.from_user.id
    
    await add_like(from_id, to_id)
    
    if await check_mutual_like(from_id, to_id):
        await callback.message.edit_text("💕 Взаимная симпатия! Вы можете написать друг другу в ЛС.")
        # Уведомляем второго
        try:
            await bot.send_message(to_id, f"💕 У вас взаимная симпатия с пользователем {from_id}!")
        except:
            pass
    else:
        await callback.answer("Лайк отправлен! ❤️")
        await show_profile(from_id, callback)

@router.callback_query(F.data.startswith("skip_"))
async def process_skip(callback: CallbackQuery):
    await callback.message.delete()
    await show_profile(callback.from_user.id, callback)

@router.callback_query(F.data.startswith("complaint_"))
async def start_complaint(callback: CallbackQuery):
    from aiogram.fsm.context import FSMContext
    from keyboards import get_complaint_reasons
    # Импортируем здесь, чтобы избежать циклического импорта, или вынесем состояние в complaints.py
    # Для простоты передадим ID в data
    await callback.message.edit_text("Выбери причину жалобы:", reply_markup=get_complaint_reasons(int(callback.data.split("_")[1])))