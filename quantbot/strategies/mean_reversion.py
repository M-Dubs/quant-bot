# quantbot/strategies/mean_reversion.py
import pandas as pd
from .base import Strategy

class MeanReversion(Strategy):
    def __init__(self, lookback=20, z_entry=1.0, z_exit=0.2):
        self.lb, self.ze, self.zx = lookback, z_entry, z_exit

    def generate_targets(self, bars) -> dict:
        out = {}
        for sym, df in bars.items():
            if len(df) < self.lb + 1: 
                continue
            close = df["close"]
            mu = close.rolling(self.lb).mean().iloc[-1]
            sd = close.rolling(self.lb).std(ddof=0).iloc[-1]
            if sd == 0 or pd.isna(sd): 
                continue
            z = (close.iloc[-1] - mu) / sd
            # simple: short when rich, long when cheap
            if z > self.ze: out[sym] = -0.005
            elif z < -self.ze: out[sym] = +0.005
            elif abs(z) < self.zx: out[sym] = 0.0
        return out
