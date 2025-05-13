import telebot
from src.gh_secrets import TELEGRAM_TOKEN

bot = telebot.TeleBot(TELEGRAM_TOKEN)

CURRENCY = "USD"

SPREADSHEET_NAME = 'cap'
TARGET_RANGE = 'D8:G19'
STOCKS_RANGE = 'B9:B25'

SHEET_DASHBOARD = 1
SHEET_STRATEGY = 3

TARGET_COL = ['25%', '50%', '75%', '100%', 'stock']
TARGET_1 = '25%'
TARGET_2 = '50%'
TARGET_3 = '75%'
TARGET_4 = '100%'

MARGIN = 1.05
MUTE_DAYS = 30
