# quantbot/strategies/breakout.py
from .base import Strategy

class Breakout(Strategy):
    def __init__(self, lookback=55, stop_lookback=20):
        self.lb = lookback
        self.slb = stop_lookback

    def generate_targets(self, bars) -> dict:
        out = {}
        for sym, df in bars.items():
            if len(df) < self.lb + 1:
                continue
            highN = df["high"].rolling(self.lb).max().iloc[-2]
            lowN  = df["low"].rolling(self.lb).min().iloc[-2]
            px = df["close"].iloc[-1]
            if px > highN: out[sym] = +0.005
            elif px < lowN: out[sym] = -0.005
        return out
