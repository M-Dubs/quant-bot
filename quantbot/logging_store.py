# quantbot/logging_store.py
import os
import sqlite3
from datetime import datetime
import pandas as pd

class Store:
    def __init__(self, db_path, parquet_root):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        os.makedirs(parquet_root, exist_ok=True)
        self.db = sqlite3.connect(db_path, check_same_thread=False)
        self.parquet_root = parquet_root
        self.init_schema()

    def init_schema(self):
        c = self.db.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS orders(
            order_id TEXT, ts TEXT, symbol TEXT, side TEXT, qty REAL, type TEXT, limit_price REAL, strategy TEXT, status TEXT, avg_fill_price REAL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS trades(
            trade_id TEXT, ts TEXT, symbol TEXT, side TEXT, qty REAL, price REAL, strategy TEXT, pnl_realized REAL, order_id TEXT)""")
        c.execute("""CREATE TABLE IF NOT EXISTS positions_snap(
            ts TEXT, symbol TEXT, qty REAL, avg_cost REAL, market_price REAL, unrealized_pnl REAL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS equity(
            ts TEXT, cash REAL, long_exposure REAL, short_exposure REAL, net_liq REAL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS strategy_perf(
            ts TEXT, strategy TEXT, symbol TEXT, ret_period REAL, exposure REAL, pnl_realized REAL, pnl_unrealized REAL)""")
        self.db.commit()

    def _parquet_path(self, topic):
        day = datetime.utcnow().strftime("%Y%m%d")
        p = os.path.join(self.parquet_root, topic, f"{day}.parquet")
        os.makedirs(os.path.dirname(p), exist_ok=True)
        return p

    def log_orders(self, orders):
        if not orders:
            return
        df = pd.DataFrame(orders)
        df["ts"] = pd.Timestamp.utcnow()
        df.to_sql("orders", self.db, if_exists="append", index=False)
        df.to_parquet(self._parquet_path("orders"), append=True)

    def log_positions(self, snapshot_dict):
        rows = []
        ts = pd.Timestamp.utcnow()
        for sym, d in snapshot_dict.items():
            rows.append({"ts": ts, "symbol": sym, **d})
        if rows:
            df = pd.DataFrame(rows)
            df.to_sql("positions_snap", self.db, if_exists="append", index=False)
            df.to_parquet(self._parquet_path("positions"), append=True)

    def log_equity(self, equity_dict):
        df = pd.DataFrame([{**equity_dict, "ts": pd.Timestamp.utcnow()}])
        df = df.rename(columns={"equity":"net_liq"})
        df.to_sql("equity", self.db, if_exists="append", index=False)
        df.to_parquet(self._parquet_path("equity"), append=True)
