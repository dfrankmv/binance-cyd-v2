import logging 

logging.basicConfig(filename = "run.log", 
                    filemode = "a",
                    level    = logging.INFO, 
                    format   = '%(asctime)s - %(levelname)s - %(message)s')

def error(message: str) : logging.error(message)
def info(message: str)  : logging.info(message)
def debug(message: str) : logging.debug(message)