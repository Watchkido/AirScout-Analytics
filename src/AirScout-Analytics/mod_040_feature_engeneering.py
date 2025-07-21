"""
modul2.py
Beispiel-Modul 2.
Hier können Funktionen oder Klassen für Modul 2 implementiert werden.
"""
# module/030_feature_engineering.py
from config import CONFIG
def berechne_merkmale(df):
    df['Temp_Mittelwert_10'] = df['Temperature_DHT_C'].rolling(10).mean()
    df['CO_Warnung'] = df['MQ7'] > 500
    return df

if __name__ == "__main__":
    # Code hier drunter wird nur ausgeführt wenn das Skript direkt aufgerufen wird
    pass