# quantbot/broker.py
from alpaca_trade_api.rest import REST, TimeFrame
from loguru import logger

class Broker:
    def __init__(self, api: REST, store):
        self.api = api
        self.store = store

    def get_positions_snapshot(self):
        pos = self.api.list_positions()
        snap = {p.symbol: {"qty": float(p.qty), "avg_cost": float(p.avg_entry_price)} for p in pos}
        return snap

    def get_account_equity(self):
        a = self.api.get_account()
        return {"ts": a.last_equity_at, "cash": float(a.cash), "equity": float(a.equity)}

    def get_cash(self):
        return float(self.api.get_account().cash)

    def rebalance_to_weights(self, target_weights: dict):
        acct = self.api.get_account()
        equity = float(acct.equity)
        positions = self.get_positions_snapshot()

        orders = []
        for sym, wt in target_weights.items():
            px = float(self.api.get_latest_trade(sym).price)
            target_value = equity * wt
            current_qty = positions.get(sym, {}).get("qty", 0.0)
            current_value = current_qty * px
            delta_value = target_value - current_value
            qty = int(delta_value / px)  # round to whole share
            if qty == 0:
                continue
            side = "buy" if qty > 0 else "sell"
            try:
                o = self.api.submit_order(symbol=sym, qty=abs(qty), side=side, type="market", time_in_force="day")
                logger.info(f"{sym} {side} {qty} @ mkt")
                orders.append({"symbol": sym, "side": side, "qty": abs(qty), "type": "market", "id": o.id})
            except Exception as e:
                logger.error(f"Order error {sym}: {e}")
        return orders
