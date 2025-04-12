import logging 
from rich.logging import RichHandler

def load_logger(): 
    logging.basicConfig(level=logging.DEBUG, handlers=[RichHandler()])
    logger = logging.getLogger("rich")
    return logger