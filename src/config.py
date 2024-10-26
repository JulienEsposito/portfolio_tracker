import telebot
import os
#from src.config_private import TELEGRAM_TOKEN

CURRENCY = "USD"

API_KEY = os.getenv('API_KEY')
BASE_URL = os.getenv('BASE_URL')
CHAT_ID = os.getenv('CHAT_ID')
json_file = os.getenv('JSON_FILE')
STOCK = os.getenv('STOCK')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

bot = telebot.TeleBot(TELEGRAM_TOKEN)



