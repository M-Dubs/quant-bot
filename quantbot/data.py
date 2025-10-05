# quantbot/data.py
from alpaca_trade_api.rest import TimeFrame, REST
import pandas as pd

class DataClient:
    def __init__(self, api: REST, cache_parquet_root=None):
        self.api = api
        self.cache_root = cache_parquet_root

    def fetch_bars(self, symbols, timeframe="5Min", limit=60):
        tf = getattr(TimeFrame, timeframe.replace("Min", "Minute"), TimeFrame.Minute)
        out = {}
        # Batch by 200 symbols to avoid rate limits
        for i in range(0, len(symbols), 200):
            chunk = symbols[i:i+200]
            bars = self.api.get_bars(chunk, tf, limit=limit).df
            # bars is multi-index df (symbol, timestamp)
            for sym in chunk:
                try:
                    sdf = bars.xs(sym, level="symbol").reset_index().rename(
                        columns={"timestamp":"ts","trade_count":"trades"})
                    out[sym] = sdf[["ts","open","high","low","close","volume"]].set_index("ts")
                except KeyError:
                    continue
        return out
