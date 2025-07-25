
import re
import io
import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
from config import CONFIG

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

    # Filtere die ersten X Minuten (aus config) direkt aus den Datenzeilen, bevor gespeichert wird
    tmp_csv = io.StringIO(''.join(daten_lines))
    df_tmp = pd.read_csv(tmp_csv)
    if 'DateTime' in df_tmp.columns:
        df_tmp['DateTime'] = pd.to_datetime(df_tmp['DateTime'], errors='coerce')
        min_zeit = df_tmp['DateTime'].min()
        grenze = min_zeit + pd.Timedelta(minutes=CONFIG.FILTER_MINUTEN_ERSTER_BLOCK)
        df_tmp = df_tmp[df_tmp['DateTime'] > grenze]
        # Entferne Zeilen ohne GPS-Daten (GPS_Lat, GPS_Lon, GPS_Alt == '--' oder leer)
        gps_spalten = ['GPS_Lat', 'GPS_Lon', 'GPS_Alt']
        for spalte in gps_spalten:
            if spalte in df_tmp.columns:
                df_tmp = df_tmp[~df_tmp[spalte].astype(str).isin(['--', '', 'nan', 'NaN'])]

        # Werte in der Spalte 'GPS_Course' mit mehr als 3 Ziffern auf 0 setzen
        if 'GPS_Course' in df_tmp.columns:
            def kurs_korrigieren(x):
                try:
                    # Prüfe, ob Wert eine Zahl ist und mehr als 3 Ziffern hat
                    if pd.notna(x) and str(x).isdigit() and len(str(int(float(x)))) > 3:
                        return 0
                    return x
                except Exception:
                    return x
            df_tmp['GPS_Course'] = df_tmp['GPS_Course'].apply(kurs_korrigieren)

        # Schreibe die gefilterten Daten zurück in daten_lines (ohne doppelte Zeilenumbrüche)
        daten_lines = [','.join(df_tmp.columns) + '\n']
        daten_lines += [zeile + '\n' for zeile in df_tmp.to_csv(index=False, header=False, lineterminator='\n').split('\n') if zeile.strip() != '']



# 1. verwandle die spalte DateTime und GPS_DateTime von objekt in eindatetime format




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

    # Schreibe bereinigte Datei
    with open(ziel_path, 'w', encoding='utf-8') as f:
        f.writelines(daten_lines)


    # 4. Lese die bereinigte Datei ein
    df = pd.read_csv(ziel_path)

    # Spalten DateTime und GPS_DateTime in datetime konvertieren
    for spalte in ['DateTime', 'GPS_DateTime']:
        if spalte in df.columns:
            df[spalte] = pd.to_datetime(df[spalte], errors='coerce')

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