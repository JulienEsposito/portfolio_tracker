from oauth2client.service_account import ServiceAccountCredentials
import gspread
import requests
import pandas as pd

from gh_secrets import BASE_URL, API_KEY
from config import SPREADSHEET_NAME, TARGET_RANGE, TARGET_COL 

def get_portfolio_sheet(page):
    json_file = "credentials.json"
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(json_file, scope)

    client = gspread.authorize(credentials)

    spreadsheet = client.open(SPREADSHEET_NAME)
    portfolio_sheet = spreadsheet.get_worksheet(page)

    return portfolio_sheet



def get_stock_prices(STOCK, CURRENCY):   
    params = {
        "fsyms": STOCK,
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
    

def exit_target(portfolio_sheet, df_stock):
    target = portfolio_sheet.get(TARGET_RANGE)
    df_target = pd.DataFrame(target)
    df_target['stock'] = df_stock.index

    df_target.columns = TARGET_COL 

    return df_target

