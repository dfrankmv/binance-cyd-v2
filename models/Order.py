import json

class Order:
    def __init__(self, id: str, pair: str, direction: str, action: str, qty: float, price: float, xprice: float = None, xstatus: str = None):
        self.id        = id
        self.pair      = pair
        self.direction = direction
        self.action    = action
        self.qty       = qty
        self.price     = price
        self.xprice    = xprice
        self.xstatus   = xstatus

    def is_long(self)    : return self.direction == "LONG"
    def is_short(self)   : return self.direction == "SHORT"
    def is_filled(self)  : return self.xstatus == "FILLED"
    def xdirection(self) : return "SHORT" if self.is_long() else "LONG"
    def xaction(self)    : return "SELL"  if self.is_long() else "BUY"

    def is_increase(self):
        long_cond  = self.direction == "LONG" and self.action == "BUY"
        short_cond = self.direction == "SHORT" and self.action == "SELL"
        return long_cond or short_cond

    def is_decrease(self):
        long_cond  = self.direction == "LONG" and self.action == "SELL"
        short_cond = self.direction == "SHORT" and self.action == "BUY"
        return long_cond or short_cond

    def to_dict(self):
        return {
            "id"        : self.id,
            "pair"      : self.pair,
            "direction" : self.direction,
            "action"    : self.action,
            "qty"       : self.qty,
            "price"     : self.price,
            "xprice"    : self.xprice,
            "xstatus"   : self.xstatus
        }

    def to_json(self):
        return json.dumps(self.to_dict())

    @staticmethod
    def from_dict(data: dict):
        return Order(
            id        = data["id"],
            pair      = data['pair'],
            direction = data['direction'],
            action    = data['action'],
            qty       = float(data['qty']),
            price     = float(data['price']),
            xprice    = float(data['xprice']),
            xstatus   = data['xstatus']
        )
    
    @staticmethod
    def from_json(json_str: str):
        data = json.loads(json_str)
        return Order(**data)
    
    @staticmethod
    def from_api(api_order: dict):
        return Order(
            id        = api_order["orderId"],
            pair      = api_order["symbol"],
            direction = api_order["positionSide"],
            action    = api_order["side"],
            qty       = float(api_order["origQty"]),
            price     = float(api_order["price"]),
            xprice    = float(api_order["avgPrice"]),
            xstatus   = api_order["status"]
        )
    
    @staticmethod
    def from_ws(ws_order: dict):
        return Order(
            id        = ws_order["c"],
            pair      = ws_order["s"],
            direction = ws_order["ps"],
            action    = ws_order["S"],
            qty       = float(ws_order["q"]),
            price     = float(ws_order["p"]),
            xprice    = float(ws_order["ap"]),
            xstatus   = ws_order["X"]
        )