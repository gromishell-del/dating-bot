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
    if await get_user(message.from_user.id):
        await message.answer("Ты уже зарегистрирован! Используй меню ниже 👇", reply_markup=get_main_keyboard())
        return
    await message.answer("Привет! 👋 Давай создадим анкету.\nКак тебя зовут?")
    await state.set_state(RegState.name)

@router.message(RegState.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Сколько тебе лет? (введи число)")
    await state.set_state(RegState.age)

@router.message(RegState.age)
async def process_age(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введи число (например, 19)")
        return
    await state.update_data(age=int(message.text))
    await message.answer("Выбери свой пол:", reply_markup=get_gender_keyboard())
    await state.set_state(RegState.gender)

@router.callback_query(RegState.gender, F.data.startswith("gender_"))
async def process_gender(callback: CallbackQuery, state: FSMContext):
    await state.update_data(gender="male" if callback.data == "gender_male" else "female")
    await callback.message.edit_text("На каком ты курсе?", reply_markup=get_course_keyboard())
    await state.set_state(RegState.course)

@router.callback_query(RegState.course, F.data.startswith("course_"))
async def process_course(callback: CallbackQuery, state: FSMContext):
    await state.update_data(course=callback.data.split("_")[1])
    await callback.message.edit_text("На каком факультете/в каком институте учишься?")
    await state.set_state(RegState.faculty)

@router.message(RegState.faculty)
async def process_faculty(message: Message, state: FSMContext):
    await state.update_data(faculty=message.text)
    await message.answer("Напиши пару слов о себе (интересы, хобби):")
    await state.set_state(RegState.description)

@router.message(RegState.description)
async def process_desc(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Отлично! Теперь отправь свою фотографию 📸")
    await state.set_state(RegState.photo)

@router.message(RegState.photo, F.photo)
async def process_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    photo_id = message.photo[-1].file_id # Берем фото лучшего качества
    
    await add_user(
        user_id=message.from_user.id,
        name=data["name"], age=data["age"], gender=data["gender"],
        course=data["course"], faculty=data["faculty"],
        description=data["description"], photo_id=photo_id
    )
    await message.answer("🎉 Анкета создана! Теперь можешь искать пару.", reply_markup=get_main_keyboard())
    await state.clear()

@router.message(RegState.photo)
async def bad_photo(message: Message):
    await message.answer("Это не фото. Пожалуйста, отправь именно фотографию (не файл).")