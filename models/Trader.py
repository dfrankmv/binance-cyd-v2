# import os
# import sys

# sys.path.insert(1, os.path.join(sys.path[0], "utils"))

import threading
import time

import utils.helpers as helpers
import utils.logger as logger

from BinanceAPI import BinanceAPI
from FinandyAPI import FinandyAPI
from MQueue     import MQueue
from Order      import Order
from Position   import Position
from State      import State

class Trader:
    def __init__(self, pair: str):
        self.pair = pair
        self.mqueue     = MQueue(MQueue.MODE_SUBSCRIBER)
        self.lock       = threading.Lock()
        self.processed  = False
        self.binanceAPI = BinanceAPI()
        self.finandyAPI = FinandyAPI(self.pair)
        self.state      = {
            "LONG" : State(pair, "LONG"),
            "SHORT": State(pair, "SHORT")
        }

    def update_breakeven(self, position: Position):
        self.state[position.direction].breakeven = position.breakeven

    def increment_nof_tps(self, direction: str):
        self.state[direction].nof_tps += 1

    def update_base_order_qty(self, direction: str, position: Position):
        n = helpers.get_param(self.pair, "take_profits_before_martingale")
        if self.state[direction].nof_tps % n == 0:
            factor = helpers.get_param(self.pair, "martingale_factor")
            self.state[direction].base_order_qty = factor * abs(position.size)

    def send_open_order(self, direction: str):
        logger.info(f"[Trader] {self.pair}_{direction}: Sending Trailing order")
        qty = self.state[direction].base_order_qty
        self.finandyAPI.open_signal(direction, qty)

    def send_tp_order(self, order: Order):
        logger.info(f"[Trader] {self.pair}_{order.direction}: Sending TP order")
        tp_dist  = helpers.get_param(self.pair, "take_profit_distance_percentage")
        d        = 1 if order.is_long() else -1
        tp_price = helpers.price_offset(self.pair, order.xprice, d * tp_dist)
        self.binanceAPI.post_decrease_order(self.pair, order.direction, tp_price, 2.0 * order.qty)

    def reset_trailing_if_exists_on_empty_position(self, direction: str):
        position = self.binanceAPI.get_position_info(self.pair, direction)
        self.update_breakeven(position)
        if position.size == 0:  # EMPTY POSITION
            self.state[direction].reset()
            open_orders = self.binanceAPI.get_increase_orders(self.pair, direction)
            if len(open_orders) > 0: # TRAILING EXISTS
                self.finandyAPI.close_signal(direction)
                self.send_open_order(direction)

    def on_position_increased(self, message: dict):
        position = Position.from_dict(message["position"])
        order    = Order.from_dict(message["order"])
        if self.pair == order.pair: # SIMPLE TRAILING FILLED
            logger.info(f"[Trader] {self.pair}_{order.direction}: Trailing filled")
            self.update_breakeven(position)
            self.send_tp_order(order)
            self.send_open_order(order.xdirection())
        elif abs(position.size) == 2*order.qty:  # NEW POSITION WAS OPEN ON ANOTHER PAIR
            logger.info(f"[Trader] {self.pair}_{order.direction}: New position was open on another pair... Reset trailing")
            self.reset_trailing_if_exists_on_empty_position(order.direction)
        self.state[order.direction].save()

    def on_position_decreased(self, message: dict):
        position = Position.from_dict(message["position"])
        order    = Order.from_dict(message["order"])
        if self.pair == order.pair: 
            if position.size == 0:  # IT WAS A WIN
                logger.info(f"[Trader] {self.pair}_{order.direction}: Win")
                self.state[order.direction].reset()
                open_orders_in_opposite_direction = self.binanceAPI.get_increase_orders(self.pair, order.xdirection())
                if len(open_orders_in_opposite_direction) == 0: # NO TRAILING ORDERS ON OPPOSITE DIRECTION
                    self.send_open_order(order.direction)  # OPEN NEW TRAILING ON THIS DIRECTION
            else: # IT'S JUST ANOTHER TP
                logger.info(f"[Trader] {self.pair}_{order.direction}: TP")
                self.update_breakeven(position)
                self.increment_nof_tps(order.direction)
                self.update_base_order_qty(order.direction, position)
            self.state[order.direction].save()

    def on_message(self, message: dict):
        self.lock.acquire()
        t = None
        if self.processed != True:
            match message["type"]:
                case "INCREASE_ORDER_FILLED": t = helpers.run_on_thread(self.on_position_increased, {"message": message})
                case "DECREASE_ORDER_FILLED": t = helpers.run_on_thread(self.on_position_decreased, {"message": message})
            t.join()
            self.lock.release()
            self.processed = True
        else:
            self.processed = False
            self.lock.release()

    def play(self):
        try:
            logger.info(f"[Trader] {self.pair}: Trader started")
            self.mqueue.listen(self.on_message)
        except KeyboardInterrupt as e: logger.info(f"[Trader] {self.pair}: Trader finished")