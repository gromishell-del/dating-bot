# handlers/matching.py
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from database import get_user, get_random_profile, add_like, check_mutual_like
from keyboards import get_action_keyboard
from config import BOT_TOKEN

router = Router()
bot = Bot(token=BOT_TOKEN)

@router.message(F.text == "Поиск")
async def start_search(message: Message, state: FSMContext):
    """Начало поиска пары"""
    user = await get_user(message.from_user.id)
    if not user:
        await message.answer("Сначала зарегистрируйся через /start")
        return
    
    await state.clear()
    await show_profile(message.from_user.id, message, state)

async def show_profile(current_user_id, target, state: FSMContext):
    """Показывает профиль другого пользователя"""
    profile = await get_random_profile(current_user_id)
    
    if not profile:
        text = "😔 Пока нет других анкет. Загляни позже!"
        if isinstance(target, Message):
            await target.answer(text)
        else:
            await target.edit_text(text)
        return

    # profile: 0:user_id, 1:name, 2:age, 3:gender, 4:course, 5:faculty, 6:description, 7:photo_id, 8:is_active
    
    gender_ru = "Парень" if profile[3] == "male" else "Девушка"
    course_text = f"{profile[4]} курс" if profile[4].isdigit() else profile[4]
    
    text = (
        f"👤 **{profile[1]}**, {profile[2]} лет\n"
        f"⚧ {gender_ru}\n"
        f"🎓 {course_text}, {profile[5]}\n"
        f" {profile[6]}"
    )
    
    keyboard = get_action_keyboard(profile[0])
    
    if profile[7]:  # Если есть фото
        if isinstance(target, Message):
            await target.answer_photo(
                profile[7],
                caption=text,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
        else:
            try:
                await target.message.answer_photo(
                    profile[7],
                    caption=text,
                    reply_markup=keyboard,
                    parse_mode="Markdown"
                )
                await target.message.delete()
            except:
                await target.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    else:
        if isinstance(target, Message):
            await target.answer(text, reply_markup=keyboard, parse_mode="Markdown")
        else:
            await target.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")

@router.callback_query(F.data.startswith("like_"))
async def process_like(callback: CallbackQuery, state: FSMContext):
    """Обработка лайка"""
    to_user_id = int(callback.data.split("_")[1])
    from_user_id = callback.from_user.id
    
    await add_like(from_user_id, to_user_id)
    is_mutual = await check_mutual_like(from_user_id, to_user_id)
    
    if is_mutual:
        await callback.message.edit_text(
            "💕 **ВЗАИМНАЯ СИМПАТИЯ!** 💕\n\n"
            "Вы понравились друг другу!",
            parse_mode="Markdown"
        )
        try:
            await bot.send_message(
                to_user_id,
                "💕 У вас взаимная симпатия!"
            )
        except:
            pass
    else:
        await callback.answer("❤️ Лайк отправлен!", show_alert=False)
        await show_profile(from_user_id, callback, state)

@router.callback_query(F.data.startswith("skip_"))
async def process_skip(callback: CallbackQuery, state: FSMContext):
    """Пропуск анкеты"""
    await callback.answer("Пропущено", show_alert=False)
    await callback.message.delete()
    await show_profile(callback.from_user.id, callback, state)

@router.callback_query(F.data.startswith("complaint_"))
async def start_complaint(callback: CallbackQuery, state: FSMContext):
    """Начало жалобы"""
    from keyboards import get_complaint_reasons
    user_id = int(callback.data.split("_")[1])
    await state.update_data(complaint_target=user_id)
    
    await callback.message.edit_text(
        "️ Выбери причину жалобы:",
        reply_markup=get_complaint_reasons(user_id)
    )
