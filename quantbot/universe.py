# quantbot/universe.py
import re
from alpaca_trade_api.rest import REST

EXCLUDE_PATTERNS = [r"-[BL]$", r"^BRK\.[A-B]$"]  # sample exclusions (leveraged; odd share classes)

class UniverseBuilder:
    def __init__(self, api: REST, config_path="configs/symbol_filters.yml"):
        self.api = api
        self.config_path = config_path

    def build(self):
        assets = self.api.list_assets(status="active")
        syms = []
        for a in assets:
            if not a.tradable or a.class_ != "us_equity":
                continue
            s = a.symbol
            if any(re.search(p, s) for p in EXCLUDE_PATTERNS):
                continue
            syms.append(s)
        # Optionally trim to top N by recent dollar volume (add later)
        return syms[:800]  # start with a manageable cap; tune later
