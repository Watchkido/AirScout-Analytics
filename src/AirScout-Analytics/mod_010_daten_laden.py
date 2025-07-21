# module/010_daten_laden.py
from config import CONFIG
import pandas as pd

def lade_daten(pfad):
    return pd.read_csv(pfad, comment="#")

        
if __name__ == "__main__":
    # Code hier drunter wird nur ausgeführt wenn das Skript direkt aufgerufen wird
    pass