# handlers/profile.py
from aiogram import Router, F
from aiogram.types import Message
from database import get_user
from keyboards import get_main_keyboard

router = Router()

@router.message(F.text == "👤 Моя анкета")
async def show_my_profile(message: Message):
    """Показать свою анкету"""
    user = await get_user(message.from_user.id)
    
    if not user:
        await message.answer("Сначала зарегистрируйся через /start")
        return
    
    # user: 0:user_id, 1:name, 2:age, 3:gender, 4:course, 5:faculty, 6:description, 7:photo_id, 8:is_active
    
    gender_ru = "Парень" if user[3] == "male" else "Девушка"
    course_text = f"{user[4]} курс" if user[4].isdigit() else user[4]
    
    text = (
        f"👤 **Твоя анкета**\n\n"
        f"📝 Имя: {user[1]}\n"
        f" Возраст: {user[2]} лет\n"
        f"⚧ Пол: {gender_ru}\n"
        f"🎓 Курс: {course_text}\n"
        f"🏛 Факультет: {user[5]}\n"
        f"💬 О себе: {user[6]}"
    )
    
    if user[7]:  # Если есть фото
        await message.answer_photo(
            user[7],
            caption=text,
            parse_mode="Markdown"
        )
    else:
        await message.answer(text, parse_mode="Markdown")
