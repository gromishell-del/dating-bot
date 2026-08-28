# bot.py
import asyncio
import os
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from database import init_db

# Импортируем ВСЕ роутеры
from handlers import registration, profile, matching, complaints, admin, settings

async def on_startup(app):
    await init_db()
    print("✅ База данных инициализирована!")

async def start_bot(bot: Bot):
    dp = Dispatcher(storage=MemoryStorage())
    
    # Подключаем ВСЕ обработчики
    dp.include_router(registration.router)
    dp.include_router(profile.router)  # ← ДОБАВИЛ
    dp.include_router(matching.router)
    dp.include_router(complaints.router)
    dp.include_router(admin.router)
    dp.include_router(settings.router)  # ← ДОБАВИЛ
    
    print("🤖 Telegram бот запущен!")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

async def main():
    bot = Bot(token=BOT_TOKEN)
    
    app = web.Application()
    app.on_startup.append(on_startup)
    
    async def health_check(request):
        return web.Response(text="Dating Bot is alive! 🚀")
    
    app.router.add_get('/', health_check)
    
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"🌐 Веб-сервер на порту {port}")
    
    await start_bot(bot)

if __name__ == "__main__":
    asyncio.run(main())
