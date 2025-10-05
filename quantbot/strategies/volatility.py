# quantbot/strategies/volatility.py
import numpy as np
from .base import Strategy

class VolatilityTarget(Strategy):
    def __init__(self, target_vol=0.15, lookback=60):
        self.tgt, self.lb = target_vol, lookback

    def generate_targets(self, bars) -> dict:
        # allocate more weight to symbols with lower realized vol
        out = {}
        for sym, df in bars.items():
            if len(df) < self.lb + 1:
                continue
            rets = df["close"].pct_change().dropna().iloc[-self.lb:]
            vol = np.std(rets) * np.sqrt(252)
            if vol and np.isfinite(vol) and vol > 0:
                w = min(0.005, self.tgt / (10 * vol))  # very conservative cap initially
                out[sym] = w
        return out
