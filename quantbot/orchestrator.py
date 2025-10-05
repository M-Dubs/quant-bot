# quantbot/orchestrator.py
import os, time, signal, sys, traceback
from datetime import datetime, timezone
from loguru import logger
from quantbot.universe import UniverseBuilder
from quantbot.data import DataClient
from quantbot.allocator import PortfolioAllocator
from quantbot.broker import Broker
from quantbot.logging_store import Store
from quantbot.strategies import load_strategies
from alpaca_trade_api.rest import REST

RUN = True

def handle_sig(sig, frame):
    global RUN
    logger.info(f"Received {sig}, shutting down cleanly...")
    RUN = False

signal.signal(signal.SIGINT, handle_sig)
signal.signal(signal.SIGTERM, handle_sig)

def is_market_open(api: REST):
    clk = api.get_clock()
    return getattr(clk, "is_open", False)

def seconds_to_next_bar(timeframe="5Min"):
    # naive: wake every 60s; keep simple first
    return 60

def main():
    logger.add("logs/quantbot.log", rotation="20 MB", retention="14 days", enqueue=True)

    api = REST()
    store = Store(db_path="data/sqlite/quantbot.db", parquet_root="data/parquet")
    broker = Broker(api=api, store=store)
    data = DataClient(api=api, cache_parquet_root="data/parquet")
    allocator = PortfolioAllocator(max_weight_per_symbol=0.02, gross_leverage_cap=1.0)

    strategies = load_strategies()  # returns list of (name, strategy_instance)
    universe_builder = UniverseBuilder(api=api, config_path="configs/symbol_filters.yml")

    current_universe = []
    last_universe_refresh = None

    logger.info("Starting orchestrator.")

    while RUN:
        try:
            if not is_market_open(api):
                # sleep longer off-hours; still wake periodically to catch open
                time.sleep(60)
                continue

            # Refresh universe once per session or every N minutes
            now = datetime.now(timezone.utc)
            if (not last_universe_refresh) or ((now - last_universe_refresh).seconds > 900):
                current_universe = universe_builder.build()
                last_universe_refresh = now
                logger.info(f"Universe size: {len(current_universe)} symbols")

            # Fetch latest bars for the batch
            bars = data.fetch_bars(symbols=current_universe, timeframe=os.getenv("BAR_TIMEFRAME", "5Min"))
            # Generate signals per strategy
            all_targets = []
            for name, strat in strategies:
                targets = strat.generate_targets(bars)  # dict {symbol: weight_delta or absolute weight}
                all_targets.append((name, targets))

            # Aggregate & allocate
            target_weights = allocator.combine(all_targets, cash=broker.get_cash(), positions=broker.get_positions_snapshot())

            # Transact to reach target weights
            orders = broker.rebalance_to_weights(target_weights)
            store.log_orders(orders)

            # Snapshots for PnL & equity
            store.log_positions(broker.get_positions_snapshot())
            store.log_equity(broker.get_account_equity())

            time.sleep(seconds_to_next_bar())

        except Exception as e:
            logger.error(f"Loop error: {e}\n{traceback.format_exc()}")
            time.sleep(10)  # brief backoff and continue

    logger.info("Stopped orchestrator.")

if __name__ == "__main__":
    main()
