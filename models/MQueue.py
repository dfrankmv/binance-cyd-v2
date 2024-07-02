import json
import zmq

import utils.logger as logger

class MQueue:
    MODE_PUBLISHER  = 0
    MODE_SUBSCRIBER = 1

    def __init__(self, mode: int):
        self.mode = mode
        try:
            match self.mode:
                case self.MODE_PUBLISHER:
                    self.socket = zmq.Context().socket(zmq.PUB)
                    self.socket.bind("tcp://*:5555")
                case self.MODE_SUBSCRIBER:
                    self.socket = zmq.Context().socket(zmq.SUB)
                    self.socket.connect("tcp://localhost:5555")
                    self.socket.setsockopt_string(zmq.SUBSCRIBE, "")
        except zmq.error.ZMQError as e: logger.error(f"ZeroMQ error: {e}")

    def put(self, message):
        try:
            self.socket.send_string(json.dumps(message))
        except zmq.error.ZMQError as e: logger.error(f"Error sending message: {e}")

    def listen(self, on_message):
        try: 
            while True:
                msg = self.socket.recv_string()
                on_message(json.loads(msg))
        except zmq.error.ZMQError as e:logger.error(f"Error on handling received message: {e}")