import requests
import json

import utils.config as config
import utils.helpers as helpers
import utils.logger as logger

class FinandyAPI:
    def __init__(self, pair: str):
        self.pair = pair
        self.trailing_distance = helpers.get_param(pair, "trailing_distance")

    def post_signal(self, direction: str, action: str, qty: float = None):
        headers = {"Content-Type": "application/json"}
        url = config.FINANDY_URL
        signal = {
            "name"         : config.FINANDY_NAME,
            "secret"       : config.FINANDY_SECRET,
            "symbol"       : self.pair,
            "positionSide" : direction.lower(),
            "side"         : action.lower()
        }
        if qty is not None:
            signal["open"] = {
                "amountType": "amount",
                "amount": qty,
                "scaled": {
                    "price1": {
                        "mode": "ofs",
                        "value": self.trailing_distance
                    }
                }
            }
            signal["dca"] = {
                "amountType": "amount",
                "amount": qty,
                "scaled": {
                    "price1": {
                        "mode": "ofs",
                        "value": self.trailing_distance
                    }
                }
            }
        try:
            response = requests.post(url, headers=headers, data=json.dumps(signal))
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f'[FinandyAPI] Error en la solicitud POST: {e}')
            return None

    def open_signal(self, direction: str, qty: float):
        action = "BUY" if direction == "LONG" else "SELL"
        logger.info(f"[FinandyAPI] Open signal sent to Finandy [{self.pair}, {direction}, {qty}]")
        return self.post_signal(direction, action, qty)
    
    def close_signal(self, direction: str):
        xaction = "SELL" if direction == "LONG" else "BUY"
        logger.info(f"[FinandyAPI] Close signal sent to Finandy [{self.pair}, {direction}]")
        return self.post_signal(direction, xaction)