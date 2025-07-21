"""
exceptions.py
Benutzerdefinierte Ausnahmen für das Projekt.
Hier werden eigene Exception-Klassen definiert.
"""
from config import CONFIG
# module/060_bild_generieren.py

import subprocess
import os
from datetime import datetime
import config

def generiere_bilder(df):
    os.makedirs("bilder", exist_ok=True)
    letzte = df.iloc[-1]
    prompt = f"Visualisierung bei {letzte['Temperature_DHT_C']}°C, {letzte['Humidity_RH']}% Luftfeuchte, CO: {letzte['MQ7']} ppm"
    dateiname = f"bild_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    pfad = os.path.join("bilder", dateiname)

    befehl = config.BILD_GENERATOR_BEFEHL.format(prompt=prompt, output_path=pfad)
    subprocess.run(befehl, shell=True, check=True)

    return [pfad]

if __name__ == "__main__":
    # Code hier drunter wird nur ausgeführt wenn das Skript direkt aufgerufen wird
    pass