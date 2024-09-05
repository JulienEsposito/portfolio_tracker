from datetime import datetime
import json
from collections import defaultdict

from src.config import bot
from src.config_private import json_file, CHAT_ID
from src.external_data import exit_target, get_portfolio_sheet


def selling_range(portfolio_sheet, df_crypto):
    df_target = exit_target(portfolio_sheet, df_crypto)

    selling_range_1 = {}
    for crypto, value in df_target[df_target['25%'] != '-'].set_index('crypto')['25%'].to_dict().items():
        if value != '-':
            value = value.replace(',', '.')
            value = float(value)
            selling_range_1[crypto] = (value, value * 1.05)

    selling_range_2 = {}
    for crypto, value in df_target[df_target['50%'] != '-'].set_index('crypto')['50%'].to_dict().items():
        if value != '-':
            value = value.replace(',', '.')
            value = float(value)
            selling_range_2[crypto] = (value, value * 1.05)

    selling_range_3 = {}
    for crypto, value in df_target[df_target['75%'] != '-'].set_index('crypto')['75%'].to_dict().items():
        if value != '-':
            value = value.replace(',', '.')
            value = float(value)
            selling_range_3[crypto] = (value, value * 1.05)

    selling_range_4 = {}
    for crypto, value in df_target[df_target['100%'] != '-'].set_index('crypto')['100%'].to_dict().items():
        if value != '-':
            value = value.replace(',', '.')
            value = float(value)
            selling_range_4[crypto] = (value, value * 1.05)

    return selling_range_1, selling_range_2, selling_range_3, selling_range_4

'''
def load_last_sent_messages():
    try:
        with open('last_sent_messages.json', 'r') as f:
            return json.load(f, object_pairs_hook=defaultdict)
    except FileNotFoundError:
        return defaultdict(dict)

def load_last_sent_messages():
    try:
        with open('last_sent_messages.json', 'r') as f:
            data = json.load(f, object_pairs_hook=defaultdict)
            if not data:  # check if the dictionary is empty
                return defaultdict(dict)
            else:
                return data
    except FileNotFoundError:
        return defaultdict(dict)
  '''  
def dict_with_datetimes(dct):
    new_dct = {}
    for key, value in dct.items():
        if value is not None and isinstance(value, str):
            value = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f")
        new_dct[key] = value
    return new_dct

def dict_with_datetimes(dct):
    new_dct = {}
    for key, value in dct.items():
        if value is not None and isinstance(value, str):
            value = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f")
        new_dct[key] = value
    return new_dct


def dict_to_defaultdict(dct):
    return defaultdict(dict, dct)

def load_last_sent_messages():
    try:
        with open('last_sent_messages.json', 'r') as f:
            dct = json.load(f, object_hook=dict_with_datetimes)
            return dict_to_defaultdict(dct)
    except FileNotFoundError:
        return defaultdict(dict)
    
'''   
def save_last_sent_messages(last_sent_messages):
    with open('last_sent_messages.json', 'w') as f:
        json.dump(dict(last_sent_messages), f)
''' 

def save_last_sent_messages(last_sent_messages):
    with open('last_sent_messages.json', 'w') as f:
        json.dump({crypto: {range_str: last_sent_time.isoformat() if last_sent_time else None
                             for range_str, last_sent_time in ranges.items()}
                   for crypto, ranges in last_sent_messages.items()}, f, indent=4)


def check_crypto_price_range(df_crypto):
    portfolio_sheet = get_portfolio_sheet(json_file)
    selling_range_1, selling_range_2, selling_range_3, selling_range_4 = selling_range(portfolio_sheet, df_crypto)
    current_time = datetime.now()

    last_sent_messages = load_last_sent_messages()

    for crypto, price_range in selling_range_1.items():
        if crypto in df_crypto.index:
            price = df_crypto.loc[crypto, 'USD']
            if price_range[0] <= price <= price_range[1]:
                message = f"Range 1: The {crypto} is in the selling range 25%. Current price: {price}"
                last_sent_time = last_sent_messages[crypto].get('Range 1')
                if not last_sent_time or (current_time - last_sent_time).days >= 3:
                    bot.send_message(CHAT_ID, message)
                    last_sent_messages[crypto]['Range 1'] = current_time

    for crypto, price_range in selling_range_2.items():
        if crypto in df_crypto.index:
            price = df_crypto.loc[crypto, 'USD']
            if price_range[0] <= price <= price_range[1]:
                message = f"Range 2: The {crypto} is in the selling range 50%. Current price: {price}"
                last_sent_time = last_sent_messages[crypto].get('Range 2')
                if not last_sent_time or (current_time - last_sent_time).days >= 3:
                    bot.send_message(CHAT_ID, message)
                    last_sent_messages[crypto]['Range 2'] = current_time

    for crypto, price_range in selling_range_3.items():
        if crypto in df_crypto.index:
            price = df_crypto.loc[crypto, 'USD']
            if price_range[0] <= price <= price_range[1]:
                message = f"Range 3: The {crypto} is in the selling range 75%. Current price: {price}"
                last_sent_time = last_sent_messages[crypto].get('Range 3')
                if not last_sent_time or (current_time - last_sent_time).days >= 3:
                    bot.send_message(CHAT_ID, message)
                    last_sent_messages[crypto]['Range 3'] = current_time

    for crypto, price_range in selling_range_4.items():
        if crypto in df_crypto.index:
            price = df_crypto.loc[crypto, 'USD']
            if price_range[0] <= price <= price_range[1]:
                message = f"Range 4: Ta moula est la!!! The {crypto} is in the selling range 100%. Current price: {price}"
                last_sent_time = last_sent_messages[crypto].get('Range 4')
                if not last_sent_time or (current_time - last_sent_time).days >= 3:
                    bot.send_message(CHAT_ID, message)
                    last_sent_messages[crypto]['Range 4'] = current_time
                    
    save_last_sent_messages(last_sent_messages)