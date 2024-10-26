from oauth2client.service_account import ServiceAccountCredentials
import gspread
import requests
import pandas as pd

from src.config import BASE_URL, API_KEY 
#from src.config_private import BASE_URL, API_KEY 

def get_portfolio_sheet():
    json_file = "credentials.json"
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(json_file, scope)

    client = gspread.authorize(credentials)

    spreadsheet = client.open('cap')
    portfolio_sheet = spreadsheet.get_worksheet(1)

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
    target = portfolio_sheet.get('AC9:AF26')
    df_target = pd.DataFrame(target)
    df_target['stock'] = df_stock.index

    df_target.columns = ['25%', '50%', '75%', '100%', 'stock']

    return df_target

