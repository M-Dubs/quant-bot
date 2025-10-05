import os
from dotenv import load_dotenv
from loguru import logger
from utils import setup_logging, heartbeat
from broker_alpaca import client, check_account, place_test_order, cancel_order, get_last_quote

def env(name, default=None, cast=str):
    v = os.getenv(name, default)
    return cast(v) if (v is not None and cast is not str) else v

def main():
    setup_logging()
    load_dotenv()
    logger.info("QuantBot (Alpaca) starting… Paper=%s", os.getenv("ALPACA_PAPER","1"))

    symbol = env("ALPACA_SYMBOL", "AAPL")
    notional = float(env("ALPACA_NOTIONAL", "1"))

    api = client()

    # 1) Account sanity
    acct = check_account(api)
    logger.info(f"Account status={acct['status']} cash=${acct['cash']:.2f} buying_power=${acct['buying_power']:.2f}")

    # 2) Data sanity
    quote = get_last_quote(api, symbol)
    logger.info(f"Last bar for {symbol}: {quote}")

    # 3) Place tiny test order (paper)
    try:
        order = place_test_order(api, symbol, notional)
        logger.info(f"Order submitted id={order.id} symbol={order.symbol} notional≈${notional}")
        # Optional: cancel if still open
        cancel_order(api, order.id)
    except Exception as e:
        logger.warning(f"Order submit failed (still proves auth path): {e}")

    heartbeat()
    logger.info("Alpaca smoke test complete.")

if __name__ == "__main__":
    main()
