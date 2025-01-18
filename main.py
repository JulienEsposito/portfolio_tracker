from portfolio_tracker.config import CURRENCY
from src.gh_secrets import STOCK
from portfolio_tracker.external_data import get_stock_prices
from portfolio_tracker.sell import check_stock_price_range

df_stock = get_stock_prices(STOCK, CURRENCY)
check_stock_price_range(df_stock)

