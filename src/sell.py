from datetime import datetime
from collections import defaultdict
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from gh_secrets import bot, CHAT_ID
from config import TARGET_1, TARGET_2, TARGET_3, TARGET_4, MARGIN, SPREADSHEET_NAME, CURRENCY, MUTE_DAYS
from src.external_data import exit_target, get_portfolio_sheet



def _selling_range(portfolio_sheet, df_stock):
    df_target = exit_target(portfolio_sheet, df_stock)

    selling_range_1 = {}
    for stock, value in df_target[df_target[TARGET_1] != '-'].set_index('stock')[TARGET_1].to_dict().items():
        if value != '-':
            value = value.replace(',', '.')
            value = float(value)
            selling_range_1[stock] = (value, value * MARGIN)

    selling_range_2 = {}
    for stock, value in df_target[df_target[TARGET_2] != '-'].set_index('stock')[TARGET_2].to_dict().items():
        if value != '-':
            value = value.replace(',', '.')
            value = float(value)
            selling_range_2[stock] = (value, value * MARGIN)

    selling_range_3 = {}
    for stock, value in df_target[df_target[TARGET_3] != '-'].set_index('stock')[TARGET_3].to_dict().items():
        if value != '-':
            value = value.replace(',', '.')
            value = float(value)
            selling_range_3[stock] = (value, value * MARGIN)

    selling_range_4 = {}
    for stock, value in df_target[df_target[TARGET_4] != '-'].set_index('stock')[TARGET_4].to_dict().items():
        if value != '-':
            value = value.replace(',', '.')
            value = float(value)
            selling_range_4[stock] = (value, value * MARGIN)

    return selling_range_1, selling_range_2, selling_range_3, selling_range_4


def get_last_messages_sent_sheet():
    json_file = "credentials.json"
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(json_file, scope)

    client = gspread.authorize(credentials)
    spreadsheet = client.open(SPREADSHEET_NAME)
    
    last_messages_sent_sheet = spreadsheet.get_worksheet(2)
    
    return last_messages_sent_sheet

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
    
    records = []
    for stock, ranges in last_sent_messages.items():
        for range_str, last_sent_time in ranges.items():
            records.append({
                'stock': stock,
                'range': range_str,
                'last_sent_time': last_sent_time.isoformat() if last_sent_time else None
            })
    
    last_messages_sent_sheet.update([['stock', 'range', 'last_sent_time']] + [[r['stock'], r['range'], r['last_sent_time']] for r in records])

def check_stock_price_range(df_stock):
    portfolio_sheet = get_portfolio_sheet(1)
    selling_range_1, selling_range_2, selling_range_3, selling_range_4 = _selling_range(portfolio_sheet, df_stock)
    current_time = datetime.now()

    last_sent_messages = _load_last_sent_messages()

    for stock, price_range in selling_range_1.items():
        if stock in df_stock.index:
            price = df_stock.loc[stock, CURRENCY]
            if price_range[0] <= price <= price_range[1]:
                message = f"Range 1: The {stock} is in the selling range {TARGET_1}. Current price: {price}"
                last_sent_time = last_sent_messages[stock].get('Range 1')
                if not last_sent_time or (current_time - last_sent_time).days >= MUTE_DAYS:
                    bot.send_message(CHAT_ID, message)
                    last_sent_messages[stock]['Range 1'] = current_time

    for stock, price_range in selling_range_2.items():
        if stock in df_stock.index:
            price = df_stock.loc[stock, CURRENCY]
            if price_range[0] <= price <= price_range[1]:
                message = f"Range 2: The {stock} is in the selling range {TARGET_2}. Current price: {price}"
                last_sent_time = last_sent_messages[stock].get('Range 2')
                if not last_sent_time or (current_time - last_sent_time).days >= MUTE_DAYS:
                    bot.send_message(CHAT_ID, message)
                    last_sent_messages[stock]['Range 2'] = current_time

    for stock, price_range in selling_range_3.items():
        if stock in df_stock.index:
            price = df_stock.loc[stock, CURRENCY]
            if price_range[0] <= price <= price_range[1]:
                message = f"Range 3: The {stock} is in the selling range {TARGET_3}. Current price: {price}"
                last_sent_time = last_sent_messages[stock].get('Range 3')
                if not last_sent_time or (current_time - last_sent_time).days >= MUTE_DAYS:
                    bot.send_message(CHAT_ID, message)
                    last_sent_messages[stock]['Range 3'] = current_time

    for stock, price_range in selling_range_4.items():
        if stock in df_stock.index:
            price = df_stock.loc[stock, CURRENCY]
            if price_range[0] <= price <= price_range[1]:
                message = f"Range 4: The {stock} is in the selling range {TARGET_4}. Current price: {price}"
                last_sent_time = last_sent_messages[stock].get('Range 4')
                if not last_sent_time or (current_time - last_sent_time).days >= MUTE_DAYS:
                    bot.send_message(CHAT_ID, message)
                    last_sent_messages[stock]['Range 4'] = current_time

    _save_last_sent_messages(last_sent_messages)
