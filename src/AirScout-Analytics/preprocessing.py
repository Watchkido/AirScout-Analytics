"""
006_Umweltkontrollsystem  watchkido
preprocessing.py
Funktionen zur Datenbereinigung und Vorverarbeitung.
Hier werden Funktionen zur Bereinigung, Transformation und Vorbereitung der Daten definiert.
"""
from config import CONFIG

def clean_data(df):
    # Beispiel: Entferne Zeilen mit fehlenden Werten
    return df.dropna()

        
if __name__ == "__main__":
    # Code hier drunter wird nur ausgeführt wenn das Skript direkt aufgerufen wird
    pass