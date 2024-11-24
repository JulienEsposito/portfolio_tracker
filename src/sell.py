from datetime import datetime
import json
from collections import defaultdict

from src.config import bot
#from src.config_private import json_file, CHAT_ID
from src.config import json_file, CHAT_ID
from src.external_data import exit_target, get_portfolio_sheet


def _selling_range(portfolio_sheet, df_stock):
    df_target = exit_target(portfolio_sheet, df_stock)

    selling_range_1 = {}
    for stock, value in df_target[df_target['25%'] != '-'].set_index('stock')['25%'].to_dict().items():
        if value != '-':
            value = value.replace(',', '.')
            value = float(value)
            selling_range_1[stock] = (value, value * 1.05)

    selling_range_2 = {}
    for stock, value in df_target[df_target['50%'] != '-'].set_index('stock')['50%'].to_dict().items():
        if value != '-':
            value = value.replace(',', '.')
            value = float(value)
            selling_range_2[stock] = (value, value * 1.05)

    selling_range_3 = {}
    for stock, value in df_target[df_target['75%'] != '-'].set_index('stock')['75%'].to_dict().items():
        if value != '-':
            value = value.replace(',', '.')
            value = float(value)
            selling_range_3[stock] = (value, value * 1.05)

    selling_range_4 = {}
    for stock, value in df_target[df_target['100%'] != '-'].set_index('stock')['100%'].to_dict().items():
        if value != '-':
            value = value.replace(',', '.')
            value = float(value)
            selling_range_4[stock] = (value, value * 1.05)

    return selling_range_1, selling_range_2, selling_range_3, selling_range_4


def _dict_with_datetimes(dct):
    new_dct = {}
    for key, value in dct.items():
        if value is not None and isinstance(value, str):
            value = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f")
        new_dct[key] = value
    return new_dct


def _dict_to_defaultdict(dct):
    return defaultdict(dict, dct)

import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Fonction pour accéder à la feuille de calcul spécifiée
def get_last_messages_sent_sheet():
    json_file = "credentials.json"
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(json_file, scope)

    client = gspread.authorize(credentials)
    spreadsheet = client.open('cap')
    
    # Accéder à la feuille 3 (nommée "last_messages_sent")
    last_messages_sent_sheet = spreadsheet.get_worksheet(2)
    
    return last_messages_sent_sheet

# Fonction pour charger les messages envoyés depuis la feuille de calcul
def _load_last_sent_messages():
    last_messages_sent_sheet = get_last_messages_sent_sheet()
    records = last_messages_sent_sheet.get_all_records()  # Récupérer toutes les données sous forme de liste de dictionnaires
    
    last_sent_messages = defaultdict(dict)
    
    # Convertir les données en un dictionnaire imbriqué pour faciliter la manipulation
    for record in records:
        stock = record.get('stock')
        range_str = record.get('range')
        last_sent_time = record.get('last_sent_time')
        
        if last_sent_time:
            last_sent_time = datetime.fromisoformat(last_sent_time)
        
        last_sent_messages[stock][range_str] = last_sent_time
    
    return last_sent_messages

# Fonction pour enregistrer les messages envoyés dans la feuille de calcul
def _save_last_sent_messages(last_sent_messages):
    last_messages_sent_sheet = get_last_messages_sent_sheet()
    
    # Nettoyer la feuille avant d'écrire
    last_messages_sent_sheet.clear()
    
    # Préparer les données sous forme de liste de dictionnaires
    records = []
    for stock, ranges in last_sent_messages.items():
        for range_str, last_sent_time in ranges.items():
            records.append({
                'stock': stock,
                'range': range_str,
                'last_sent_time': last_sent_time.isoformat() if last_sent_time else None
            })
    
    # Écrire les données dans la feuille de calcul
    last_messages_sent_sheet.update([['stock', 'range', 'last_sent_time']] + [[r['stock'], r['range'], r['last_sent_time']] for r in records])

# Exemple d'utilisation dans la fonction check_stock_price_range
def check_stock_price_range(df_stock):
    portfolio_sheet = get_portfolio_sheet(1)
    selling_range_1, selling_range_2, selling_range_3, selling_range_4 = _selling_range(portfolio_sheet, df_stock)
    current_time = datetime.now()

    last_sent_messages = _load_last_sent_messages()

    for stock, price_range in selling_range_1.items():
        if stock in df_stock.index:
            price = df_stock.loc[stock, 'USD']
            if price_range[0] <= price <= price_range[1]:
                message = f"Range 1: The {stock} is in the selling range 25%. Current price: {price}"
                last_sent_time = last_sent_messages[stock].get('Range 1')
                if not last_sent_time or (current_time - last_sent_time).days >= 3:
                    bot.send_message(CHAT_ID, message)
                    last_sent_messages[stock]['Range 1'] = current_time

    for stock, price_range in selling_range_2.items():
        if stock in df_stock.index:
            price = df_stock.loc[stock, 'USD']
            if price_range[0] <= price <= price_range[1]:
                message = f"Range 2: The {stock} is in the selling range 50%. Current price: {price}"
                last_sent_time = last_sent_messages[stock].get('Range 2')
                if not last_sent_time or (current_time - last_sent_time).days >= 3:
                    bot.send_message(CHAT_ID, message)
                    last_sent_messages[stock]['Range 2'] = current_time

    for stock, price_range in selling_range_3.items():
        if stock in df_stock.index:
            price = df_stock.loc[stock, 'USD']
            if price_range[0] <= price <= price_range[1]:
                message = f"Range 3: The {stock} is in the selling range 75%. Current price: {price}"
                last_sent_time = last_sent_messages[stock].get('Range 3')
                if not last_sent_time or (current_time - last_sent_time).days >= 3:
                    bot.send_message(CHAT_ID, message)
                    last_sent_messages[stock]['Range 3'] = current_time

    for stock, price_range in selling_range_4.items():
        if stock in df_stock.index:
            price = df_stock.loc[stock, 'USD']
            if price_range[0] <= price <= price_range[1]:
                message = f"Range 4: Ta moula est la!!! The {stock} is in the selling range 100%. Current price: {price}"
                last_sent_time = last_sent_messages[stock].get('Range 4')
                if not last_sent_time or (current_time - last_sent_time).days >= 3:
                    bot.send_message(CHAT_ID, message)
                    last_sent_messages[stock]['Range 4'] = current_time

    _save_last_sent_messages(last_sent_messages)
