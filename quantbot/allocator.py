# quantbot/allocator.py
from collections import defaultdict

class PortfolioAllocator:
    def __init__(self, max_weight_per_symbol=0.02, gross_leverage_cap=1.0):
        self.max_w = max_weight_per_symbol
        self.gross_cap = gross_leverage_cap

    def combine(self, strategy_targets, cash, positions) -> dict:
        """
        strategy_targets: list of (strategy_name, {symbol: target_contribution})
        returns absolute weights per symbol, normalized and clipped
        """
        agg = defaultdict(float)
        for _, targets in strategy_targets:
            for sym, w in targets.items():
                agg[sym] += w

        # clip per symbol
        for sym in list(agg.keys()):
            agg[sym] = max(min(agg[sym], self.max_w), -self.max_w)

        # normalize gross exposure
        gross = sum(abs(w) for w in agg.values())
        if gross > self.gross_cap and gross > 0:
            scale = self.gross_cap / gross
            for sym in agg:
                agg[sym] *= scale

        return dict(agg)
