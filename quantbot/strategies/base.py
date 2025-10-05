# quantbot/strategies/base.py
from abc import ABC, abstractmethod

class Strategy(ABC):
    @abstractmethod
    def generate_targets(self, bars) -> dict:
        """
        bars: dict[symbol] -> pandas.DataFrame with columns [open, high, low, close, volume]
        returns: dict[symbol] -> target weight contribution (can be -1..+1)
        """
        ...
