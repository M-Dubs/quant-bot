import os
import backoff
from loguru import logger
from alpaca_trade_api import REST, TimeFrame

def _base_url():
    paper = os.getenv("ALPACA_PAPER", "1") == "1"
    return "https://paper-api.alpaca.markets" if paper else "https://api.alpaca.markets"

def client():
    key = os.environ["ALPACA_KEY_ID"]
    secret = os.environ["ALPACA_SECRET_KEY"]
    return REST(key_id=key, secret_key=secret, base_url=_base_url())

@backoff.on_exception(backoff.expo, Exception, max_tries=5)
def check_account(api: REST):
    acct = api.get_account()
    return {"status": acct.status, "cash": float(acct.cash), "buying_power": float(acct.buying_power)}

@backoff.on_exception(backoff.expo, Exception, max_tries=5)
def place_test_order(api: REST, symbol: str, notional: float):
    # MARKET day order for tiny notional on paper = safe connectivity test
    # If you prefer absolutely-no-fill, switch to limit with far-from-market price.
    return api.submit_order(symbol=symbol, notional=notional, side="buy", type="market", time_in_force="day")

def cancel_order(api: REST, order_id: str):
    try:
        api.cancel_order(order_id)
    except Exception as e:
        logger.warning(f"Cancel may have failed/filled already: {e}")

def get_last_quote(api: REST, symbol: str):
    # quick market data sanity via data API v2 (built into SDK)
    bar = api.get_bars(symbol, TimeFrame.Minute, limit=1).df
    return None if bar.empty else bar.tail(1).to_dict("records")[0]
