"""
mod_040_feature_engeneering.py
Feature Engineering für Gassensor-Daten:
- Lädt die erste CSV aus 'data/bearbeitet0' in ein DataFrame
- Erstellt Zeit-Features (Jahr, Monat, Tag, Wochentag, Stunde, Minute, Sekunde, millisec) aus GPS_DateTime und SecSinceMidnight-MS
- Speichert das Ergebnis als CSV in 'data/ergebnisse/{dateiname}/feature_{dateiname}.csv', als TXT in 'data/ergebnisse', und als CSV in 'data/bearbeitet2'
"""

# Kompatibler Import für Direktaufruf und als Modul
import sys
import os
import pandas as pd
from datetime import datetime
import re
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=Warning)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import CONFIG

def feature_engineering():



    # 1. Lade die erste CSV aus dem Ordner
    csv_dir = r"E:\dev\projekt_python_venv\airscout-analytics\data\bearbeitet0"
    ergebnisse_dir = r"E:\dev\projekt_python_venv\airscout-analytics\data\ergebnisse"
    csv_files = [f for f in os.listdir(csv_dir) if f.lower().endswith('.csv')]
    if not csv_files:
        print(f"Keine CSV-Datei in {csv_dir} gefunden!")
        return None
    csv_path = os.path.join(csv_dir, csv_files[0])

    featureengeneering = pd.read_csv(csv_path)

    # Robust: Spalten-Mapping für verschiedene Namensvarianten
    spalten_mapping = {
        'DateTime_MESZ': 'DateTime',
        'DateTime_UTC': 'GPS_DateTime',
        'SecSinceMidnightMS': 'SecSinceMidnight-MS',
        'SecSinceMidnightMS': 'SecSinceMidnight-MS',
        # ggf. weitere Zuordnungen ergänzen
    }
    # Nur Spalten umbenennen, die auch existieren
    vorhandene_mappings = {k: v for k, v in spalten_mapping.items() if k in featureengeneering.columns}
    if vorhandene_mappings:
        featureengeneering.rename(columns=vorhandene_mappings, inplace=True)


    # 2. Neue Zeitspalten aus GPS_DateTime und SecSinceMidnight-MS
    if 'GPS_DateTime' in featureengeneering.columns:
        featureengeneering['GPS_DateTime'] = pd.to_datetime(featureengeneering['GPS_DateTime'], errors='coerce')
        featureengeneering['Jahr'] = featureengeneering['GPS_DateTime'].dt.year
        featureengeneering['Monat'] = featureengeneering['GPS_DateTime'].dt.month
        featureengeneering['Tag'] = featureengeneering['GPS_DateTime'].dt.day
        # Wochentag als ausgeschriebener Name (z.B. Montag)
        try:
            featureengeneering['Wochentag'] = featureengeneering['GPS_DateTime'].dt.day_name(locale='de_DE')
        except TypeError:
            # Fallback falls locale nicht unterstützt wird (z.B. auf Windows ohne de_DE)
            wochentage = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag']
            featureengeneering['Wochentag'] = featureengeneering['GPS_DateTime'].dt.weekday.apply(lambda x: wochentage[x] if pd.notna(x) else None)
        featureengeneering['Stunde'] = featureengeneering['GPS_DateTime'].dt.hour
        featureengeneering['Minute'] = featureengeneering['GPS_DateTime'].dt.minute
        featureengeneering['Sekunde'] = featureengeneering['GPS_DateTime'].dt.second
        # Cast Zeitspalten explizit auf Int32
        for spalte in ['Jahr', 'Monat', 'Tag', 'Stunde', 'Minute', 'Sekunde', 'millisec']:
            if spalte in featureengeneering.columns:
                featureengeneering[spalte] = featureengeneering[spalte].astype('Int32')
    else:
        print('Spalte GPS_DateTime nicht gefunden!')


    # Millisekunden aus SecSinceMidnight-MS extrahieren
    if 'SecSinceMidnight-MS' in featureengeneering.columns:
        def extract_millisec(val):
            try:
                # Format: Sekunden-Millisekunden, z.B. 12345-678
                if pd.isna(val):
                    return None
                parts = str(val).split('-')
                if len(parts) == 2 and parts[1].isdigit():
                    return int(parts[1])
                return None
            except Exception:
                return None
        featureengeneering['millisec'] = featureengeneering['SecSinceMidnight-MS'].apply(extract_millisec)
    else:
        print('Spalte SecSinceMidnight-MS nicht gefunden!')

    # Straßennamen-Feature einfügen (vor dem Speichern)
    featureengeneering = strassennamen_einfügen(featureengeneering)

    # Prüfe, ob 'street' wirklich enthalten ist
    if 'street' not in featureengeneering.columns:
        print("[Fehler] Spalte 'street' wurde nicht hinzugefügt!")
    else:
        print("[Info] Spalte 'street' erfolgreich hinzugefügt und wird gespeichert.")

    # 3. Speichern als CSV und TXT
    basename = os.path.basename(csv_path)
    name_ohne_ext = os.path.splitext(basename)[0]
    out_csv_name = f"feature_{basename}"
    out_csv_path = os.path.join(ergebnisse_dir, name_ohne_ext, out_csv_name)
    out_txt_path = os.path.join(ergebnisse_dir, f"feature_{name_ohne_ext}.txt")

    # Zusätzlich im Ordner bearbeitet1 speichern
    bearbeitet1_dir = r"E:\dev\projekt_python_venv\airscout-analytics\data\bearbeitet1"
    os.makedirs(bearbeitet1_dir, exist_ok=True)
    out_bearbeitet1_path = os.path.join(bearbeitet1_dir, out_csv_name)
    featureengeneering.to_csv(out_bearbeitet1_path, index=False, encoding='utf-8')

    # Ordner für CSV anlegen
    os.makedirs(os.path.dirname(out_csv_path), exist_ok=True)
    featureengeneering.to_csv(out_csv_path, index=False, encoding='utf-8')

    # TXT-Export: Schreibe DataFrame als Text (Kopf und Statistik)
    with open(out_txt_path, 'w', encoding='utf-8') as f:
        f.write(f"Feature Engineering Ergebnis für Datei: {basename}\n\n")
        f.write("Spalten:\n")
        f.write(', '.join(featureengeneering.columns) + '\n\n')
        f.write("Kopf der Daten:\n")
        f.write(featureengeneering.head().to_string() + '\n\n')
        f.write("Statistik:\n")
        f.write(featureengeneering.describe(include='all').to_string())

    print(f"Feature-Engineering abgeschlossen. CSV: {out_csv_path}\nTXT: {out_txt_path}\nAuch gespeichert in: {out_bearbeitet1_path}")
    return featureengeneering


def strassennamen_einfügen(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fügt eine Spalte 'street' in das DataFrame ein, basierend auf GPS-Koordinaten.
    Vergleicht GPS_Lat und GPS_Lon mit datenbank/GPS2Street.csv und trägt den Straßennamen ein.
    Falls keine Übereinstimmung: 'Unbekannt'.

    :param df: DataFrame mit Spalten 'GPS_Lat' und 'GPS_Lon'
    :return: DataFrame mit neuer Spalte 'street'
    """
    gps2street_path = os.path.join(os.path.dirname(__file__), '..', '..', 'datenbank', 'GPS2Street.csv')
    if not os.path.exists(gps2street_path):
        print(f"[Warnung] GPS2Street.csv nicht gefunden: {gps2street_path}")
        df['street'] = 'Unbekannt'
        return df
    streets = pd.read_csv(gps2street_path)
    # Prüfe, ob alle benötigten Spalten vorhanden sind
    benoetigte_spalten = {'GPS_Lat', 'GPS_Lon', 'street'}
    fehlende = benoetigte_spalten - set(streets.columns)
    if fehlende:
        print(f"[Fehler] Die folgenden Spalten fehlen in GPS2Street.csv: {fehlende}")
        df['street'] = 'Unbekannt'
        return df
    streets = streets.dropna(subset=['GPS_Lat', 'GPS_Lon', 'street'])
    # Erstelle Lookup-Dict für exakte Zuordnung
    lookup = {(round(row['GPS_Lat'], 6), round(row['GPS_Lon'], 6)): row['street'] for _, row in streets.iterrows()}

    # Hilfsfunktion: Haversine-Distanz in Metern
    from math import radians, sin, cos, sqrt, atan2
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371000  # Erdradius in Metern
        phi1, phi2 = radians(lat1), radians(lat2)
        dphi = radians(lat2 - lat1)
        dlambda = radians(lon2 - lon1)
        a = sin(dphi/2)**2 + cos(phi1)*cos(phi2)*sin(dlambda/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return R * c

    # Liste aller bekannten Koordinaten
    street_coords = streets[['GPS_Lat', 'GPS_Lon']].values
    street_names = streets['street'].values


    def finde_strasse_unscharf(lat, lon, radius=10.0):
        key = (round(lat, 6), round(lon, 6))
        # Erst exaktes Matching
        if key in lookup:
            return lookup[key]
        # Sonst: Nächstgelegene Straße im Umkreis suchen
        min_dist = float('inf')
        best_street = 'Unbekannt'
        for (lat2, lon2), name in zip(street_coords, street_names):
            dist = haversine(lat, lon, lat2, lon2)
            if dist < min_dist:
                min_dist = dist
                best_street = name
        if min_dist <= radius:
            return best_street
        return 'Unbekannt'

    if 'GPS_Lat' in df.columns and 'GPS_Lon' in df.columns:
        df['street'] = [
            finde_strasse_unscharf(lat, lon)
            if pd.notna(lat) and pd.notna(lon) else 'Unbekannt'
            for lat, lon in zip(df['GPS_Lat'], df['GPS_Lon'])
        ]
    else:
        df['street'] = 'Unbekannt'

    return df






# === Einstiegspunkt ===
def main():
    """
    Pipeline-kompatibler Einstiegspunkt: Führt main_plotting() aus.
    """
    return feature_engineering()




if __name__ == "__main__":
    main()