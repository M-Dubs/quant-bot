import os
from dotenv import load_dotenv
from loguru import logger
from utils import setup_logging, heartbeat
from broker_gemini import get_exchange, ping_public, auth_balance, place_test_order, cancel_order

def env(name, default=None, cast=str):
    v = os.getenv(name, default)
    return cast(v) if v is not None and cast is not str else v

def main():
    setup_logging()
    load_dotenv()
    logger.info("QuantBot starting (Gemini)…")

    symbol      = env("SYMBOL", "BTC/USD")
    test_amt    = float(env("TEST_AMOUNT", "0.0001"))
    test_price  = float(env("TEST_PRICE", "10000"))

    ex = get_exchange()

    # 1) Public ping
    t = ping_public(ex)
    logger.info(f"Public ticker OK: {t.get('symbol')} last={t.get('last')}")

    # 2) Auth check
    bal = auth_balance(ex)
    # Show only totals (avoid dumping full structure)
    total_usd = bal.get("total", {}).get("USD", 0)
    total_btc = bal.get("total", {}).get("BTC", 0)
    logger.info(f"Auth OK. Total USD={total_usd}, BTC={total_btc}")

    # 3) Place a POST-ONLY far-from-market order (should remain unfilled)
    logger.info(f"Placing test POST-ONLY LIMIT BUY {symbol} amount={test_amt} price={test_price}")
    try:
        order = place_test_order(ex, symbol, test_amt, test_price)
        logger.info(f"Order placed: id={order.get('id') or order.get('order_id')}")
        oid = order.get("id") or order.get("order_id")
    except Exception as e:
        logger.warning(f"Order placement rejected (this still proves auth/permissions): {e}")
        oid = None

    # 4) Cancel it if we got an id
    if oid:
        try:
            cancel = cancel_order(ex, symbol, oid)
            logger.info(f"Cancel response: {cancel}")
        except Exception as e:
            logger.warning(f"Cancel error: {e}")

    heartbeat()
    logger.info("Test sequence complete.")

if __name__ == "__main__":
    main()
