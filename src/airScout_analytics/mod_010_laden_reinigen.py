def main():
    """
    Pipeline-kompatibler Einstiegspunkt: Führt laden_und_reinigen() aus und gibt das DataFrame zurück.
    """
    return laden_und_reinigen()
"""mod_010_laden_reinigen.py
Lädt die erste CSV aus 'data/bearbeitet', bereinigt sie und speichert das Ergebnis in 'data/bearbeitet0'.
Gibt das bereinigte DataFrame zurück.   
"""




import re
import io
import os
import glob
import pandas as pd

# Kompatibler Import für Direktaufruf und als Modul
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import CONFIG
import matplotlib.pyplot as plt
import airScout_analytics.context as context





def laden_und_reinigen():
    """
    Lädt die erste CSV aus data/bearbeitet, bereinigt sie und speichert das Ergebnis in data/bearbeitet0.
    Gibt das bereinigte DataFrame zurück.
    """
    # 1. hole die erste gefundene csv datei aus dem Ordner ../data/bearbeitet
    projekt_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    bearbeitet_ordner = os.path.join(projekt_root, "data", "bearbeitet")
    csv_files = glob.glob(os.path.join(bearbeitet_ordner, "*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"Keine CSV-Datei in {bearbeitet_ordner} gefunden!")
    csv_path = csv_files[0]
    basename = os.path.basename(csv_path)



    # 2. Finde die Headerzeile explizit, überspringe Schritt wenn nicht vorhanden
    header_name = "SecSinceMidnight-MS,Temperature_DHT_C,Humidity_RH,Light_Level,Light_Percent,GPS_Lat,GPS_Lon,GPS_Alt,GPS_Speed,GPS_Course,GPS_Sats,MQ2,MQ3,MQ4,MQ5,MQ6,MQ7,MQ8,MQ9,MQ135,Mic1,Mic2,Radiation_CPS,DateTime,GPS_DateTime"
    with open(csv_path, encoding='utf-8') as f:
        lines = f.readlines()

    # Suche nach Headerzeile, ignoriere Zeilen mit # davor
    header_row = None
    for i, line in enumerate(lines):
        if line.strip().startswith('#'):
            continue
        if line.strip() == header_name:
            header_row = i
            break
    if header_row is None:
        header_row = 0

    # 3. Ersetze ; durch , und entferne ' MESZ' und ' UTC' in den Datenzeilen (ab Header)
    daten_lines = []
    for zeile in lines[header_row:]:
        zeile = zeile.replace(';', ',')
        zeile = zeile.replace(' MESZ', '')
        zeile = zeile.replace(' UTC', '')
        daten_lines.append(zeile)

    # Lese die Daten direkt in ein DataFrame ein
    tmp_csv = io.StringIO(''.join(daten_lines))
    df = pd.read_csv(tmp_csv)

    # Spalten DateTime und GPS_DateTime in datetime konvertieren (früh, damit Filter funktionieren)
    for spalte in ['DateTime', 'GPS_DateTime']:
        if spalte in df.columns:
            df[spalte] = pd.to_datetime(df[spalte], errors='coerce')

    # Filtere die ersten X Minuten (aus config) direkt aus dem DataFrame
    if 'DateTime' in df.columns:
        min_zeit = df['DateTime'].min()
        grenze = min_zeit + pd.Timedelta(minutes=CONFIG.FILTER_MINUTEN_ERSTER_BLOCK)
        df = df[df['DateTime'] > grenze]

    # Entferne Zeilen ohne GPS-Daten (GPS_Lat, GPS_Lon, GPS_Alt == '--' oder leer)
    gps_spalten = ['GPS_Lat', 'GPS_Lon', 'GPS_Alt']
    for spalte in gps_spalten:
        if spalte in df.columns:
            df = df[~df[spalte].astype(str).isin(['--', '', 'nan', 'NaN'])]

    # Werte in der Spalte 'GPS_Course' mit mehr als 3 Ziffern auf 0 setzen
    if 'GPS_Course' in df.columns:
        def kurs_korrigieren(x):
            try:
                # Prüfe, ob Wert eine Zahl ist und mehr als 3 Ziffern hat
                if pd.notna(x) and str(x).isdigit() and len(str(int(float(x)))) > 3:
                    return 0
                return x
            except Exception:
                return x
        df['GPS_Course'] = df['GPS_Course'].apply(kurs_korrigieren)

    # Entferne alle Zeilen, in denen GPS_Lon < 8 ist
    if 'GPS_Lon' in df.columns:
        df['GPS_Lon'] = pd.to_numeric(df['GPS_Lon'], errors='coerce')
        vorher = len(df)
        df = df[df['GPS_Lon'] >= 8]
        nachher = len(df)
        print(f"Gefiltert: {vorher - nachher} Zeilen mit GPS_Lon < 8 entfernt.")

    # Entferne die letzte Zeile vor dem Abspeichern (z.B. fehlerhafte Messungen am Dateiende)
    if len(df) > 3:
        df = df.iloc[:-1]

    # ------------------------------------------------------------------------------
    # Zielordner und neuen Dateinamen bestimmen
    zielordner = os.path.join(projekt_root, "data", "bearbeitet0")
    os.makedirs(zielordner, exist_ok=True)
    # Extrahiere Zeitstempel aus dem alten Dateinamen
    basename = os.path.basename(csv_path)
    match = re.search(r'(\d{4})_(\d{2})(\d{2})(\d{2})(\d{2})', basename)
    if match:
        jahr, monat, tag, stunde, minute = match.groups()
        neuer_name = f"{jahr}_{monat}_{tag}_{stunde}_{minute}.csv"
    else:
        # Fallback: nimm alles nach dem letzten Unterstrich und hänge .csv an
        neuer_name = basename.split('_')[-1].replace('.csv', '') + ".csv"
    ziel_path = os.path.join(zielordner, neuer_name)

    # Dateinamen ohne .csv-Endung extrahieren und global speichern
    context.filename_ohne_ext = os.path.splitext(neuer_name)[0]
    print("Datei name:", context.filename_ohne_ext)
    # Schreibe den Wert als Python-Variable in src/airScout_analytics/context.py
    context_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "context.py")
    with open(context_path, "w", encoding="utf-8") as f:
        f.write(f"filename_ohne_ext = '{context.filename_ohne_ext}'\n")

    # Schreibe bereinigtes DataFrame als CSV
    df.to_csv(ziel_path, index=False, encoding='utf-8', lineterminator='\n')

    # Anzeigeoptionen für bessere Terminaldarstellung
    pd.set_option('display.width', 120)
    pd.set_option('display.max_columns', 10)

    return df

if __name__ == "__main__":
    df = laden_und_reinigen()
    print('Spaltennamen:', list(df.columns))
    print(df.head())
    print("\nStatistik (transponiert):")
    print(df.describe().T.to_string())
    # Nur numerische Spalten für das Histogramm auswählen
    num_cols = df.select_dtypes(include=['number', 'datetime']).columns
    if len(num_cols) > 0:
        df[num_cols].hist(figsize=(10, 6))
        # plt.show()  # Deaktiviert, damit das Skript nicht blockiert
    else:
        print("Keine numerischen Spalten für Histogramm gefunden.")
    print("Fertig!")