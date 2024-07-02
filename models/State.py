import os
import sys
import time

sys.path.insert(1, os.path.join(sys.path[0], "utils"))

import utils.helpers as helpers

class State:
    def __init__(self, pair: str, direction: str):
        default_state_dict = {
            "timestamp"     : time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "base_order_qty": helpers.get_param(pair, "base_order_qty"),
            "breakeven"     : None,
            "nof_tps"       : 0
        }
        self.filepath = f"states/state_{pair.lower()}_{direction.lower()}.json"
        helpers.create_file_if_not_exists(self.filepath, default_state_dict)
        state_dict = helpers.get_dict_from_file(self.filepath)
        self.pair           = pair
        self.direction      = direction
        self.timestamp      = state_dict["timestamp"]
        self.nof_tps        = state_dict["nof_tps"]
        self.base_order_qty = state_dict["base_order_qty"]
        self.breakeven      = state_dict["breakeven"]
        
    def save(self):
        self.timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        helpers.file_rewrite_dict(self.filepath, self.to_dict())

    def to_dict(self):
        return {
            "timestamp"     : self.timestamp,
            "base_order_qty": self.base_order_qty,
            "breakeven"     : self.breakeven,
            "nof_tps"       : self.nof_tps
        }
    
    def reset(self):
        self.timestamp      = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.base_order_qty = helpers.get_param(self.pair, "base_order_qty")
        self.breakeven      = None 
        self.nof_tps        = 0
