from datetime import datetime
from collections import defaultdict
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from src.gh_secrets import CHAT_ID
from portfolio_tracker.config import bot, TARGET_1, TARGET_2, TARGET_3, TARGET_4, MARGIN, SPREADSHEET_NAME, CURRENCY, MUTE_DAYS, SHEET_STRATEGY
from portfolio_tracker.external_data import exit_target, get_portfolio_sheet

TARGETS = [TARGET_1, TARGET_2, TARGET_3, TARGET_4]

def _selling_range(portfolio_sheet, df_stock):
    ranges = {}
    df_target = exit_target(portfolio_sheet, df_stock)

    for target in TARGETS:
        selling_range = {}
        for stock, value in df_target[df_target[target] != '-'].set_index('stock')[target].to_dict().items():
            if value != '-':
                value = float(value.replace(',', '.'))
                selling_range[stock] = (value, value * MARGIN)
        ranges[target] = selling_range

    return ranges

def get_last_messages_sent_sheet():
    json_file = "credentials.json"
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(json_file, scope)

    client = gspread.authorize(credentials)
    spreadsheet = client.open(SPREADSHEET_NAME)
    return spreadsheet.get_worksheet(2)

def _load_last_sent_messages():
    last_messages_sent_sheet = get_last_messages_sent_sheet()
    records = last_messages_sent_sheet.get_all_records()
    
    last_sent_messages = defaultdict(dict)
    
    for record in records:
        stock = record.get('stock')
        range_str = record.get('range')
        last_sent_time = record.get('last_sent_time')
        
        if last_sent_time:
            last_sent_time = datetime.fromisoformat(last_sent_time)
        
        last_sent_messages[stock][range_str] = last_sent_time
    
    return last_sent_messages

def _save_last_sent_messages(last_sent_messages):
    last_messages_sent_sheet = get_last_messages_sent_sheet()
    last_messages_sent_sheet.clear()
    
    records = [
        {
            'stock': stock,
            'range': range_str,
            'last_sent_time': last_sent_time.isoformat() if last_sent_time else None
        }
        for stock, ranges in last_sent_messages.items()
        for range_str, last_sent_time in ranges.items()
    ]
    
    last_messages_sent_sheet.update([['stock', 'range', 'last_sent_time']] + [[r['stock'], r['range'], r['last_sent_time']] for r in records])

def check_stock_price_range(df_stock):
    portfolio_sheet = get_portfolio_sheet(SHEET_STRATEGY)
    selling_ranges = _selling_range(portfolio_sheet, df_stock)
    current_time = datetime.now()

    last_sent_messages = _load_last_sent_messages()

    for target in TARGETS:
        for stock, price_range in selling_ranges[target].items():
            if stock in df_stock.index:
                price = df_stock.loc[stock, CURRENCY]
                if price_range[0] <= price <= price_range[1]:
                    message = f"{stock} reach the price {price} you have to sell {target}"
                    last_sent_time = last_sent_messages[stock].get(target)
                    if not last_sent_time or (current_time - last_sent_time).days >= MUTE_DAYS:
                        bot.send_message(CHAT_ID, message)
                        last_sent_messages[stock][target] = current_time

    _save_last_sent_messages(last_sent_messages)
