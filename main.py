from portfolio_tracker.config import CURRENCY
from portfolio_tracker.external_data import get_stock_prices, get_stocks
from portfolio_tracker.sell import check_stock_price_range

stocks = get_stocks()
df_stock = get_stock_prices(stocks, CURRENCY)
check_stock_price_range(df_stock)

