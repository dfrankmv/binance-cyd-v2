import binance
import time
import websocket

import utils.config as config
import utils.logger as logger

import binance.enums
import binance.exceptions

from Position import Position
from Order    import Order

class BinanceAPI:
    def __init__(self):
        self.client = binance.Client(config.BINANCE_API_KEY, config.BINANCE_SECRET_KEY)
        self.ws_listen_key = ""
        self.ws_app: websocket.WebSocketApp = None

    def get_position_info(self, pair: str, direction: str):
        try:
            positions = self.client.futures_position_information(symbol=pair)
            position  = next(filter(lambda pos: direction == pos["positionSide"], positions))
            breakeven = float(position["breakEvenPrice"])
            size      = float(position["positionAmt"])
            return Position(pair, direction, breakeven, size)
        except binance.exceptions.BinanceAPIException as e   : logger.error("[BinanceAPI] Error de API de Binance: %s", e.message)
        except binance.exceptions.BinanceOrderException as e : logger.error("[BinanceAPI] Error en la orden de Binance: %s", e.message)
        except Exception as e                                : logger.error("[BinanceAPI] Ha ocurrido un error: %s", e)
    
    def post_order(self, pair: str, direction: str, action: str, price: float, qty: float):
        try:
            order = self.client.futures_create_order(
                symbol       = pair,
                side         = action,
                type         = binance.enums.ORDER_TYPE_LIMIT,
                timeInForce  = binance.enums.TIME_IN_FORCE_GTC,
                quantity     = qty,
                price        = price,
                positionSide = direction 
            )
            return Order.from_api(order)
        except binance.exceptions.BinanceAPIException as e   : logger.error(f"[BinanceAPI] Error de API de Binance: {e.message}")
        except binance.exceptions.BinanceOrderException as e : logger.error(f"[BinanceAPI] Error en la orden de Binance: {e.message}")
        except Exception as e                                : logger.error(f"[BinanceAPI] Ha ocurrido un error: {e}")
    
    def get_open_orders(self, pair: str, direction: str = None, action: str = None) -> list[Order]:
        try:
            open_orders = self.client.futures_get_open_orders(symbol=pair)
            res = []
            for o in open_orders:
                cond = True 
                cond = cond and o["type"] == "LIMIT"
                cond = cond and (direction is None or o["positionSide"] == direction)
                cond = cond and (action is None or o["side"] == action)
                if cond: res.append(Order.from_api(o))
            return res
        except binance.exceptions.BinanceAPIException as e   : logger.error("[BinanceAPI] Error de API de Binance: %s", e.message)
        except binance.exceptions.BinanceOrderException as e : logger.error("[BinanceAPI] Error en la orden de Binance: %s", e.message)
        except Exception as e                                : logger.error("[BinanceAPI] Ha ocurrido un error: %s", e)
    
    def delete_open_orders(self, pair: str, direction: str = None, action: str = None) -> None:
        try:
            open_orders = self.get_open_orders(pair, direction, action)
            for order in open_orders:
                self.client.futures_cancel_order(symbol=pair, orderId=order.id)
        except binance.exceptions.BinanceAPIException as e   : logger.error("[BinanceAPI] Error de API de Binance: %s", e.message)
        except binance.exceptions.BinanceOrderException as e : logger.error("[BinanceAPI] Error en la orden de Binance: %s", e.message)
        except Exception as e                                : logger.error("[BinanceAPI] Ha ocurrido un error: %s", e)
    
    def set_ws_listen_key(self):
        try:
            listen_key = self.client.futures_stream_get_listen_key()
            logger.info(f"[BinanceAPI] Listen key: {listen_key}")
            self.listen_key = listen_key
        except Exception as e: logger.error(f"[BinanceAPI] Error on getting listen key: {e}")

    def keep_ws_alive(self):
        while True:
            try:
                time.sleep(30 * 60)  # 30 mins
                self.client.futures_stream_keepalive(self.listen_key)
                logger.info("[BinanceAPI] Listen key renewed.")
            except Exception as e:
                logger.error(f"[BinanceAPI] Error on renewing listen key: {e}")
                break
            except KeyboardInterrupt: 
                logger.info("[BinanceAPI] keep_ws_alive() interrupted.")

    def set_ws_app(self, on_message):
        self.ws_app    = websocket.WebSocketApp(
            url        = f"wss://fstream.binance.com/ws/{self.listen_key}", 
            on_message = on_message,
            on_open    = lambda ws                : logger.info( f"[BinanceAPI] WebSocket opened"),
            on_close   = lambda ws, code, message : logger.info( f"[BinanceAPI] WebSocket closed"),
            on_error   = lambda ws, error         : logger.error(f"[BinanceAPI] WebSocket error: {error}")
        )

    def get_increase_orders(self, pair: str, direction: str):
        action = "BUY" if direction == "LONG" else "SELL"
        return self.get_open_orders(pair, direction, action)
    
    def delete_increase_orders(self, pair: str, direction: str):
        action = "BUY" if direction == "LONG" else "SELL"
        self.delete_open_orders(pair, direction, action)
        logger.info(f"[BinanceAPI] Increase orders were canceled [{pair}, {direction}]")

    def post_decrease_order(self, pair: str, direction: str, price: float, qty: float):
        xaction = "SELL" if direction == "LONG" else "BUY"
        self.post_order(pair, direction, xaction, price, qty)
        logger.info(f"[BinanceAPI] Decrease order posted [{pair} {direction} {xaction} {qty}@{price}]")
    
