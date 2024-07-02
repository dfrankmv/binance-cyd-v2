import sys
import os

sys.path.insert(1, os.path.join(sys.path[0], "models"))
sys.path.insert(1, os.path.join(sys.path[0], "models", "utils"))

from models.Trader import Trader

if len(sys.argv) < 2:
    print("Use: python trading.py <PAIR>")
    sys.exit(1)

pair = sys.argv[1]
trader = Trader(pair)
trader.play()