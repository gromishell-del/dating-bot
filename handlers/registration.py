# handlers/registration.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import get_user, add_user
from keyboards import get_gender_keyboard, get_course_keyboard, get_main_keyboard

router = Router()

class RegState(StatesGroup):
    name = State()
    age = State()
    gender = State()
    course = State()
    faculty = State()
    description = State()
    photo = State()

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    # Сбрасываем состояние
    await state.clear()
    
    # Проверяем, зарегистрирован ли пользователь
    user = await get_user(message.from_user.id)
    
    if user:
        await message.answer(
            "Ты уже зарегистрирован! 👍\n\n"
            "Используй кнопки внизу для навигации:",
            reply_markup=get_main_keyboard()
        )
        return
    
    await message.answer(
        "Привет! 👋\n"
        "Давай создадим твою анкету для знакомств.\n\n"
        "Как тебя зовут?"
    )
    await state.set_state(RegState.name)

@router.message(RegState.name)
async def process_name(message: Message, state: FSMContext):
    """Обработка имени"""
    if len(message.text) < 2:
        await message.answer("Имя слишком короткое. Напиши своё имя полностью:")
        return
    
    await state.update_data(name=message.text.strip())
    await message.answer("Сколько тебе лет? (введи число, например: 20)")
    await state.set_state(RegState.age)

@router.message(RegState.age)
async def process_age(message: Message, state: FSMContext):
    """Обработка возраста"""
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введи число (например: 19 или 20):")
        return
    
    age = int(message.text)
    if age < 16 or age > 100:
        await message.answer("Возраст должен быть от 16 до 100 лет. Попробуй ещё раз:")
        return
    
    await state.update_data(age=age)
    await message.answer(
        "Выбери свой пол:",
        reply_markup=get_gender_keyboard()
    )
    await state.set_state(RegState.gender)

@router.callback_query(RegState.gender, F.data.startswith("gender_"))
async def process_gender(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора пола"""
    gender = "male" if callback.data == "gender_male" else "female"
    await state.update_data(gender=gender)
    
    await callback.message.edit_text(
        "На каком ты курсе?",
        reply_markup=get_course_keyboard()
    )
    await state.set_state(RegState.course)

@router.callback_query(RegState.course, F.data.startswith("course_"))
async def process_course(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора курса"""
    course = callback.data.split("_")[1]
    await state.update_data(course=course)
    
    await callback.message.edit_text(
        "На каком факультете/в каком институте учишься?\n"
        "(например: ИТ, Экономический, Юридический)"
    )
    await state.set_state(RegState.faculty)

@router.message(RegState.faculty)
async def process_faculty(message: Message, state: FSMContext):
    """Обработка факультета"""
    if len(message.text) < 3:
        await message.answer("Напиши название факультета подробнее:")
        return
    
    await state.update_data(faculty=message.text.strip())
    await message.answer(
        "Напиши пару слов о себе:\n"
        "интересы, хобби, что ищешь\n"
        "(можно пропустить, нажав 'Пропустить')"
    )
    await state.set_state(RegState.description)

@router.message(RegState.description)
async def process_description(message: Message, state: FSMContext):
    """Обработка описания"""
    description = message.text.strip()
    if description.lower() in ['пропустить', 'skip', '-']:
        description = "Не указано"
    
    await state.update_data(description=description)
    await message.answer(
        "Отлично! 📸\n"
        "Теперь отправь свою фотографию.\n"
        "(Отправь как фото, не как файл)"
    )
    await state.set_state(RegState.photo)

@router.message(RegState.photo, F.photo)
async def process_photo(message: Message, state: FSMContext):
    """Обработка фотографии"""
    data = await state.get_data()
    
    # Берём фото наилучшего качества (последнее в списке)
    photo_id = message.photo[-1].file_id
    
    # Добавляем пользователя в базу
    await add_user(
        user_id=message.from_user.id,
        name=data["name"],
        age=data["age"],
        gender=data["gender"],
        course=data["course"],
        faculty=data["faculty"],
        description=data["description"],
        photo_id=photo_id
    )
    
    await message.answer(
        "🎉 Поздравляю! Анкета создана!\n\n"
        "Теперь ты можешь:\n"
        "• Искать пару 🔍\n"
        "• Просмотреть свою анкету 👤\n\n"
        "Удачи! 💕",
        reply_markup=get_main_keyboard()
    )
    
    await state.clear()

@router.message(RegState.photo)
async def bad_photo(message: Message):
    """Если отправлено не фото"""
    await message.answer(
        "Это не фотография 📷\n"
        "Пожалуйста, отправь именно фото (не файл, не документ)."
    )
