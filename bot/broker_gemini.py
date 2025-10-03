import os
import ccxt
from loguru import logger

def get_exchange():
    # CCXT Gemini instance
    ex = ccxt.gemini({
        "apiKey": os.getenv("GEMINI_API_KEY"),
        "secret": os.getenv("GEMINI_API_SECRET"),
        "enableRateLimit": True,
        # Gemini doesn’t need passphrase; IP allowlist is configured on the website if you want.
        "options": {
            "createMarketBuyOrderRequiresPrice": False
        }
    })
    return ex

def ping_public(ex):
    # simple public call
    return ex.fetch_ticker("BTC/USD")

def auth_balance(ex):
    return ex.fetch_balance()

def place_test_order(ex, symbol: str, amount: float, price: float):
    """
    Safe test: POST-ONLY limit order far from market so it won’t fill.
    If the venue rejects postOnly, CCXT will raise; that still proves auth + placement.
    """
    params = {"postOnly": True}
    return ex.create_order(symbol, "limit", "buy", amount, price, params)

def cancel_order(ex, symbol: str, order_id: str):
    try:
        return ex.cancel_order(order_id, symbol)
    except Exception as e:
        logger.warning(f"Cancel failed (maybe already rejected/not placed): {e}")
        return None
