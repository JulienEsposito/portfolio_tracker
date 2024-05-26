from src.config import CRYPTO, CURRENCY
from src.external_data import get_crypto_prices
from src.sell import check_crypto_price_range

df_crypto = get_crypto_prices(CRYPTO, CURRENCY)
check_crypto_price_range(df_crypto)