# logger che scrive nel file BitcoinTree.log
import logging
import os
from datetime import datetime
from pathlib import Path
from colorama import Fore, Style

# Configurazione del logger
def setup_logger():
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "BitcoinTree.log"

    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Log di avvio
    logging.info("Logger initialized at %s", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
def log_info(message):
    logging.info(message)
    
def log_alert(message):
    logging.warning(message)
    

def log_error(message):
    logging.error(message)
    


def log_exception(e):   
    logging.exception("Exception occurred: %s", str(e))
    
# Inizializza il logger
setup_logger()
if __name__ == "__main__":
    # Esempio di utilizzo del logger
    log_info("This is an info message.")
    log_alert("This is a alert message.")
    log_error("This is an error message.")
    
    try:
        1 / 0  # Provoca un'eccezione per testare il logger
    except Exception as e:
        log_exception(e)
    log_exception("This is a test exception.")