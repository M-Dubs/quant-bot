# quantbot/strategies/__init__.py
from .mean_reversion import MeanReversion
from .breakout import Breakout
from .ma_crossover import MovingAverageCrossover
from .momentum import Momentum
from .volatility import VolatilityTarget

def load_strategies():
    return [
        ("mean_rev", MeanReversion(lookback=20, z_entry=1.0, z_exit=0.2)),
        ("breakout", Breakout(lookback=55, stop_lookback=20)),
        ("ma_x", MovingAverageCrossover(short=20, long=50)),
        ("momentum", Momentum(lookback=126, top_n=50, per_symbol_cap=0.01)),
        ("vol_target", VolatilityTarget(target_vol=0.15, lookback=60)),
    ]
