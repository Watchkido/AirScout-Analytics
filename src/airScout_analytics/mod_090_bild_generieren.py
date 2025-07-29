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
import sys
import importlib
import pandas as pd
import glob

def generiere_bilder(df):
    os.makedirs("bilder", exist_ok=True)
    letzte = df.iloc[-1]
    prompt = f"Visualisierung bei {letzte['Temperature_DHT_C']}°C, {letzte['Humidity_RH']}% Luftfeuchte, CO: {letzte['MQ7']} ppm"
    dateiname = f"bild_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    pfad = os.path.join("bilder", dateiname)

    befehl = config.BILD_GENERATOR_BEFEHL.format(prompt=prompt, output_path=pfad)
    subprocess.run(befehl, shell=True, check=True)

    return [pfad]

def main() -> bool:
    """
    Pipeline-kompatibler Einstiegspunkt: Lädt DataFrame und generiert ein Bild.
    """
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    context = importlib.import_module('airScout_analytics.context')
    filename_ohne_ext = getattr(context, 'filename_ohne_ext', None)
    if not filename_ohne_ext:
        print("[Fehler] context.filename_ohne_ext ist nicht gesetzt!")
        return False
    # Lade die erste CSV aus bearbeitet3
    datenordner = os.path.join("data", "bearbeitet3")
    csv_dateien = glob.glob(os.path.join(datenordner, "*.csv"))
    if not csv_dateien:
        print(f"Keine CSV-Dateien in {datenordner} gefunden.")
        return False
    pfad = csv_dateien[0]
    try:
        df = pd.read_csv(pfad)
    except Exception as e:
        print(f"Fehler beim Laden der CSV: {e}")
        return False
    bilder = generiere_bilder(df)
    if bilder:
        print(f"✅ Bild generiert: {bilder[0]}")
        return True
    print("[Fehler] Kein Bild generiert.")
    return False


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Fehler bei der Bildgenerierung: {e}")