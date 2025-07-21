"""
006_Umweltkontrollsystem  watchkido
preprocessing.py
Funktionen zur Datenbereinigung und Vorverarbeitung.
Hier werden Funktionen zur Bereinigung, Transformation und Vorbereitung der Daten definiert.
"""
from config import CONFIG

# module/050_text_generieren.py

def generiere_text(df):
    letzte = df.iloc[-1]
    text = (
        f"📅 Umweltbericht am {letzte['DateTime']}:\n"
        f"🌡 Temperatur: {letzte['Temperature_DHT_C']}°C\n"
        f"💧 Luftfeuchtigkeit: {letzte['Humidity_RH']}%\n"
        f"🔥 CO-Konzentration: {letzte['MQ7']} ppm\n"
    )
    if letzte['CO_Warnung']:
        text += "⚠️ Warnung: Kritischer CO-Wert erkannt!"
    return [text]

if __name__ == "__main__":
    # Code hier drunter wird nur ausgeführt wenn das Skript direkt aufgerufen wird
    pass