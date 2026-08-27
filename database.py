# database.py
import aiosqlite

DB_NAME = "dating_bot.db"

async def init_db():
    """Создаёт таблицы при первом запуске"""
    async with aiosqlite.connect(DB_NAME) as db:
        # Таблица пользователей
        await db.execute("""CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            name TEXT, age INTEGER, gender TEXT, course INTEGER,
            faculty TEXT, description TEXT, photo_id TEXT,
            is_active INTEGER DEFAULT 1
        )""")
        # Таблица лайков
        await db.execute("""CREATE TABLE IF NOT EXISTS likes (
            from_user_id INTEGER, to_user_id INTEGER
        )""")
        # Таблица жалоб
        await db.execute("""CREATE TABLE IF NOT EXISTS complaints (
            from_user_id INTEGER, to_user_id INTEGER, reason TEXT
        )""")
        await db.commit()

async def add_user(user_id, name, age, gender, course, faculty, description, photo_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""INSERT INTO users (user_id, name, age, gender, course, faculty, description, photo_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", 
            (user_id, name, age, gender, course, faculty, description, photo_id))
        await db.commit()

async def get_user(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
            return await cursor.fetchone()

async def get_random_profile(current_user_id):
    """Получает случайного активного пользователя, кроме себя"""
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("""
            SELECT * FROM users WHERE user_id != ? AND is_active = 1 
            ORDER BY RANDOM() LIMIT 1
        """, (current_user_id,)) as cursor:
            return await cursor.fetchone()

async def add_like(from_id, to_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT INTO likes (from_user_id, to_user_id) VALUES (?, ?)", (from_id, to_id))
        await db.commit()

async def check_mutual_like(user1_id, user2_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("""
            SELECT COUNT(*) FROM likes WHERE 
            (from_user_id = ? AND to_user_id = ?) OR (from_user_id = ? AND to_user_id = ?)
        """, (user1_id, user2_id, user2_id, user1_id)) as cursor:
            return (await cursor.fetchone())[0] == 2

async def add_complaint(from_id, to_id, reason):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT INTO complaints (from_user_id, to_user_id, reason) VALUES (?, ?, ?)", (from_id, to_id, reason))
        await db.commit()

async def get_all_complaints():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT * FROM complaints") as cursor:
            return await cursor.fetchall()

async def ban_user(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE users SET is_active = 0 WHERE user_id = ?", (user_id,))
        await db.commit()

async def get_all_users():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT * FROM users") as cursor:
            return await cursor.fetchall()