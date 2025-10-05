# quantbot/strategies/ma_crossover.py
from .base import Strategy

class MovingAverageCrossover(Strategy):
    def __init__(self, short=20, long=50):
        self.s, self.l = short, long

    def generate_targets(self, bars) -> dict:
        out = {}
        for sym, df in bars.items():
            if len(df) < self.l + 1: 
                continue
            sma_s = df["close"].rolling(self.s).mean().iloc[-1]
            sma_l = df["close"].rolling(self.l).mean().iloc[-1]
            if sma_s > sma_l: out[sym] = +0.005
            elif sma_s < sma_l: out[sym] = -0.005
        return out
