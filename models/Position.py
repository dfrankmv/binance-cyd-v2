import json

class Position:
    def __init__(self, pair: str, direction: str, breakeven: float, size: float):
        self.pair       = pair
        self.direction  = direction
        self.breakeven  = breakeven
        self.size       = size

    def is_long(self):  return self.direction == "LONG"
    def is_short(self): return self.direction == "SHORT"
    
    def to_dict(self):
        return {
            "pair"      : self.pair,
            "direction" : self.direction,
            "breakeven" : self.breakeven,
            "size"      : self.size
        }

    def to_json(self): 
        return json.dumps(self.to_dict())

    @staticmethod
    def from_dict(data: dict):
        return Position(
            pair      = data['pair'],
            direction = data['direction'],
            breakeven = data["breakeven"],
            size      = data["size"]
        )
    
    @staticmethod
    def from_json(json_str: str):
        data = json.loads(json_str)
        return Position(**data)
    