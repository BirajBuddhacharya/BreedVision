import logging 
from rich.logging import RichHandler

def load_logger(): 
    logging.basicConfig(level=logging.DEBUG, handlers=[RichHandler(markup = True)])
    logger = logging.getLogger("rich")
    return logger