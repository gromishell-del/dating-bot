# config.py
import os

# Render будет брать токен из настроек сайта, а если их нет — использовать этот (для тестов на ПК)
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8802244642:AAGmHxUnWpKAJMR2pCj8FP2K8crW52wdxns")

# То же самое для ID админа
ADMIN_ID_STR = os.environ.get("ADMIN_IDS", "1344423827")
ADMIN_IDS = [int(ADMIN_ID_STR)]