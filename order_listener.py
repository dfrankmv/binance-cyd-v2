import sys
import os

sys.path.insert(1, os.path.join(sys.path[0], "models"))
sys.path.insert(1, os.path.join(sys.path[0], "models", "utils"))

from models.BinanceWS import BinanceWS

binance_ws = BinanceWS()

binance_ws.start()