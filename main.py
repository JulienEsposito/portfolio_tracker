from config import CURRENCY
from gh_secrets import STOCK
from src.external_data import get_stock_prices
from src.sell import check_stock_price_range

df_stock = get_stock_prices(STOCK, CURRENCY)
check_stock_price_range(df_stock)

