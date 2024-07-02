import json
import time

import utils.helpers as helpers
import utils.logger as logger

from BinanceAPI import BinanceAPI
from MQueue     import MQueue
from Order      import Order

class BinanceWS:
    def __init__(self):
        self.api        = BinanceAPI()
        self.mqueue     = MQueue(MQueue.MODE_PUBLISHER)
        self.api.set_ws_listen_key()
        self.api.set_ws_app(self.on_message)

    def on_message(self, ws, message: str):
        helpers.run_on_thread(self.handle_message, {"message": message})
    
    def handle_message(self, message):
        try:
            message = json.loads(message)
            print(message)
            if "o" in message and message["o"]["X"] == "FILLED":
                order    = Order.from_ws(message["o"])
                position = self.api.get_position_info(order.pair, order.direction)
                payload  = {
                    "order": order.to_dict(),
                    "position": position.to_dict()
                }
                logger.info(f"[BinanceWS] New order filled: {message}")
                logger.info(f"[BinanceWS] Order: {order.to_json()}")
                logger.info(f"[BinanceWS] Position: {position.to_json()}")
                if order.is_increase(): payload["type"] = "INCREASE_ORDER_FILLED"
                if order.is_decrease(): payload["type"] = "DECREASE_ORDER_FILLED"
                self.mqueue.put(payload)
        except Exception as e: logger.error(f"Error on processing message: {e}")
        except KeyboardInterrupt as e: logger.info(f"handle_message() interrupted.")

    def start(self):
        helpers.run_on_thread(self.api.keep_ws_alive)
        helpers.run_on_thread(self.api.ws_app.run_forever)
        try:
            while True: time.sleep(1)
        except KeyboardInterrupt:
            self.api.ws_app.close()
            logger.info("WebSocket stopped and program ended.")
        except Exception as e:
            self.api.ws_app.close()
            logger.error(f"Error in main program: {e}")
            exit(1)

