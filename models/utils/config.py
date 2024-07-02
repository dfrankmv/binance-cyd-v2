import configparser

config = configparser.ConfigParser()
config.read("config.ini")

BINANCE_API_KEY    = config["binance"]["api_key"]
BINANCE_SECRET_KEY = config["binance"]["secret_key"]
FINANDY_URL        = config["finandy"]["url"]
FINANDY_NAME       = config["finandy"]["name"]
FINANDY_SECRET     = config["finandy"]["secret"]