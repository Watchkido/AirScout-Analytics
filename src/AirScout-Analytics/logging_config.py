"""
logging_config.py
Konfiguration für das Logging-System.
Hier wird das Logging-Format und Level festgelegt.
"""
from config import CONFIG
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        
if __name__ == "__main__":
    # Code hier drunter wird nur ausgeführt wenn das Skript direkt aufgerufen wird
    pass