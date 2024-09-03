from oauth2client.service_account import ServiceAccountCredentials
import gspread
import requests
import pandas as pd
import datetime
import json
from collections import defaultdict

from src.config import CRYPTO, CURRENCY
from src.config_private import BASE_URL, API_KEY, CHAT_ID


def get_portfolio_sheet(json_file):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(json_file, scope)

    client = gspread.authorize(credentials)

    spreadsheet = client.open('cap')
    portfolio_sheet = spreadsheet.get_worksheet(1)

    return portfolio_sheet



def get_crypto_prices(fsyms, tsyms):   
    params = {
        "fsyms": CRYPTO,
        "tsyms": CURRENCY,
        "api_key": API_KEY
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data).transpose()
        return df
    else:
        print("Error during API request :", response.status_code)
        return None
    

def exit_target(portfolio_sheet, df_crypto):
    target = portfolio_sheet.get('AC9:AF35')
    df_target = pd.DataFrame(target)
    df_target['crypto'] = df_crypto.index

    df_target.columns = ['25%', '50%', '75%', '100%', 'crypto']

    return df_target

