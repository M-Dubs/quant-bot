# quantbot/strategies/momentum.py
import numpy as np
from .base import Strategy

class Momentum(Strategy):
    def __init__(self, lookback=126, top_n=50, per_symbol_cap=0.01):
        self.lb, self.top_n, self.cap = lookback, top_n, per_symbol_cap

    def generate_targets(self, bars) -> dict:
        # rank by total return over lookback, long top_n, short bottom_n (optional)
        ranks = []
        for sym, df in bars.items():
            if len(df) < self.lb + 1: 
                continue
            r = df["close"].iloc[-1] / df["close"].iloc[-(self.lb+1)] - 1
            ranks.append((sym, r))
        ranks.sort(key=lambda x: x[1], reverse=True)
        longs = {sym: min(self.cap, 0.005) for sym, _ in ranks[: self.top_n]}
        return longs
