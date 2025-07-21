# lade nacheinander alle .csv dateien aus date/roh
# lösche den gesamten text über den überschriften
# lösche dann alle Zeilen mit NULL-Werten
# speichere die gereinigte Datei im Ordner data/bearbeitet0
# module/020_daten_reinigen.py
from config import CONFIG
import pandas as pd

def reinige_daten(df):
    df = df[df['Temperature_DHT_C'].notna()]
    df['DateTime'] = pd.to_datetime(df['DateTime'], errors='coerce')
    df = df.dropna(subset=['DateTime'])
    return df
