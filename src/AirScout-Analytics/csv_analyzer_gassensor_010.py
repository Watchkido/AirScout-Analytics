# 📊 VERBESSERTER CSV ANALYSER FÜR GASSENSOR-DATEN
import pandas as pd
import numpy as np
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Import der Konfiguration
from config import CONFIG

# Lade CSV-Analyzer Konfiguration
HIGH_CORRELATION_THRESHOLD = CONFIG.CSV_ANALYZER['HIGH_CORRELATION_THRESHOLD']
DEFAULT_CSV_FOLDER = CONFIG.CSV_ANALYZER['DEFAULT_CSV_FOLDER']
ENVIRONMENTAL_KEYWORDS = CONFIG.CSV_ANALYZER['ENVIRONMENTAL_KEYWORDS']
TIME_KEYWORDS = CONFIG.CSV_ANALYZER['TIME_KEYWORDS']
MQ_SENSOR_IDENTIFIER = CONFIG.CSV_ANALYZER['MQ_SENSOR_IDENTIFIER']
REPORT_ENCODING = CONFIG.CSV_ANALYZER['REPORT_ENCODING']
DECIMAL_PLACES = CONFIG.CSV_ANALYZER['DECIMAL_PLACES']
FILE_SIZE_UNIT = CONFIG.CSV_ANALYZER['FILE_SIZE_UNIT']
OUTPUT_SUFFIXES = CONFIG.CSV_ANALYZER['OUTPUT_SUFFIXES']

def parse_sensor_csv(csv_filepath):
    """
    Robuster Parser für kommentierte CSV-Dateien mit Gassensor-Daten
    """
    print(f"🔍 Analysiere Datei: {csv_filepath}")
    
    # Datei einlesen und Header suchen
    with open(csv_filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Suche nach der ersten nicht-kommentierten Zeile mit Kommas
    header_line = None
    data_start = None
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line.startswith('#') and ',' in line:
            if header_line is None:
                header_line = i
                print(f"📋 Header gefunden in Zeile {i + 1}: {line[:80]}...")
            else:
                data_start = i
                break
    
    if header_line is None:
        print("❌ Kein CSV-Header gefunden!")
        return None
    
    # CSV mit korrekt erkanntem Header laden
    try:
        df = pd.read_csv(csv_filepath, skiprows=header_line)
        print(f"✅ CSV erfolgreich geladen: {df.shape[0]} Zeilen × {df.shape[1]} Spalten")
        return df
    except Exception as e:
        print(f"❌ Fehler beim Laden: {e}")
        return None

def analyse_gassensor_data(df, output_pfad):
    """
    Spezielle Analyse für Gassensor-Daten
    """
    print("\n🔬 GASSENSOR-DATENANALYSE")
    print("=" * 50)
    
    # MQ-Sensoren identifizieren
    mq_spalten = [col for col in df.columns if MQ_SENSOR_IDENTIFIER in col.upper()]
    print(f"🎯 {len(mq_spalten)} MQ-Gassensoren gefunden: {', '.join(mq_spalten)}")
    
    # Umweltsensoren identifizieren
    umwelt_spalten = []
    for col in df.columns:
        col_lower = col.lower()
        if any(keyword in col_lower for keyword in ENVIRONMENTAL_KEYWORDS):
            umwelt_spalten.append(col)
    print(f"🌡️ {len(umwelt_spalten)} Umweltsensoren: {', '.join(umwelt_spalten)}")
    
    # Zeitanalyse
    zeit_spalten = [col for col in df.columns if any(keyword in col.lower() for keyword in TIME_KEYWORDS)]
    print(f"⏰ {len(zeit_spalten)} Zeitspalten: {', '.join(zeit_spalten)}")
    
    # Statistiken der MQ-Sensoren
    if mq_spalten:
        print("\n📊 MQ-SENSOR STATISTIKEN")
        print("-" * 40)
        mq_stats = df[mq_spalten].describe()
        print(mq_stats.round(DECIMAL_PLACES))
        
        # Variabilität der Sensoren
        print("\n📈 SENSOR-VARIABILITÄT (Standardabweichung)")
        print("-" * 40)
        variabilitaet = df[mq_spalten].std().sort_values(ascending=False)
        for sensor, std_val in variabilitaet.items():
            print(f"{sensor:>6}: {std_val:8.{DECIMAL_PLACES}f}")
        
        # Korrelationen zwischen MQ-Sensoren
        if len(mq_spalten) > 1:
            print("\n🔗 MQ-SENSOR KORRELATIONEN")
            print("-" * 40)
            korr_matrix = df[mq_spalten].corr()
            
            # Höchste Korrelationen finden
            high_corr = []
            for i in range(len(korr_matrix.columns)):
                for j in range(i+1, len(korr_matrix.columns)):
                    corr_val = korr_matrix.iloc[i, j]
                    if abs(corr_val) > HIGH_CORRELATION_THRESHOLD:
                        sensor1 = korr_matrix.columns[i]
                        sensor2 = korr_matrix.columns[j]
                        high_corr.append((sensor1, sensor2, corr_val))
            
            if high_corr:
                threshold_text = f"🔥 Hohe Korrelationen (|r| > {HIGH_CORRELATION_THRESHOLD}):"
                print(threshold_text)
                for s1, s2, corr in sorted(high_corr, key=lambda x: abs(x[2]), reverse=True):
                    print(f"  {s1} ↔ {s2}: {corr:6.3f}")
            else:
                print("✅ Keine sehr hohen Korrelationen zwischen MQ-Sensoren")
    
    return {
        'mq_sensoren': mq_spalten,
        'umwelt_sensoren': umwelt_spalten,
        'zeit_spalten': zeit_spalten,
        'total_sensoren': len(mq_spalten) + len(umwelt_spalten)
    }

def create_detailed_report(df, csv_filepath, sensor_info):
    """
    Erstellt einen detaillierten Analysereport als TXT und CSV
    """
    base_name = os.path.splitext(csv_filepath)[0]
    info_filename = f"{base_name}{OUTPUT_SUFFIXES['INFO_TXT']}"
    csv_filename = f"{base_name}{OUTPUT_SUFFIXES['INFO_CSV']}"
    
    content = []
    content.append("=" * 80)
    content.append(f"GASSENSOR-DATENANALYSE REPORT")
    content.append(f"Datei: {os.path.basename(csv_filepath)}")
    content.append(f"Erstellt: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    content.append("=" * 80)
    
    # Grunddaten
    content.append(f"\n🔍 1. GRUNDLEGENDE INFORMATIONEN")
    content.append("-" * 40)
    content.append(f"📊 Datensätze: {df.shape[0]:,}")
    content.append(f"📋 Spalten gesamt: {df.shape[1]}")
    content.append(f"🎯 MQ-Gassensoren: {len(sensor_info['mq_sensoren'])}")
    content.append(f"🌡️ Umweltsensoren: {len(sensor_info['umwelt_sensoren'])}")
    content.append(f"⏰ Zeitfelder: {len(sensor_info['zeit_spalten'])}")
    
    # Spaltenübersicht
    content.append(f"\n📋 2. SPALTEN-ÜBERSICHT")
    content.append("-" * 40)
    for i, col in enumerate(df.columns, 1):
        dtype = str(df[col].dtype)
        null_count = df[col].isnull().sum()
        unique_count = df[col].nunique()
        content.append(f"{i:2d}. {col:<20} | {dtype:<8} | {null_count:>4} NULL | {unique_count:>6} eindeutig")
    
    # MQ-Sensor Details
    if sensor_info['mq_sensoren']:
        content.append(f"\n🎯 3. MQ-GASSENSOR DETAILS")
        content.append("-" * 40)
        mq_stats = df[sensor_info['mq_sensoren']].describe()
        content.append(mq_stats.round(DECIMAL_PLACES).to_string())
    
    # Umweltdaten
    if sensor_info['umwelt_sensoren']:
        content.append(f"\n🌡️ 4. UMWELTSENSOR DETAILS")
        content.append("-" * 40)
        umwelt_stats = df[sensor_info['umwelt_sensoren']].describe()
        content.append(umwelt_stats.round(DECIMAL_PLACES).to_string())
    
    # Zeitreihen-Info
    if sensor_info['zeit_spalten']:
        content.append(f"\n⏰ 5. ZEITREIHEN-INFORMATIONEN")
        content.append("-" * 40)
        for zeit_col in sensor_info['zeit_spalten']:
            if 'DateTime' in zeit_col:
                try:
                    erste_zeit = df[zeit_col].iloc[0]
                    letzte_zeit = df[zeit_col].iloc[-1]
                    content.append(f"📅 {zeit_col}:")
                    content.append(f"   Start: {erste_zeit}")
                    content.append(f"   Ende:  {letzte_zeit}")
                except:
                    content.append(f"📅 {zeit_col}: (Zeitformat-Analyse fehlgeschlagen)")
    
    # Qualitätsbewertung
    content.append(f"\n✅ 6. DATENQUALITÄT")
    content.append("-" * 40)
    total_cells = df.size
    null_cells = df.isnull().sum().sum()
    completeness = ((total_cells - null_cells) / total_cells) * 100
    content.append(f"📊 Vollständigkeit: {completeness:.1f}%")
    content.append(f"❌ Fehlende Werte: {null_cells:,} von {total_cells:,}")
    
    # Speichern der TXT-Datei
    with open(info_filename, 'w', encoding=REPORT_ENCODING) as f:
        f.write('\n'.join(content))
    
    # CSV-Export der Analyseergebnisse erstellen
    csv_data = []
    
    # Grundinformationen
    csv_data.append(['Kategorie', 'Parameter', 'Wert'])
    csv_data.append(['Grunddaten', 'Datensätze', df.shape[0]])
    csv_data.append(['Grunddaten', 'Spalten_gesamt', df.shape[1]])
    csv_data.append(['Grunddaten', 'MQ_Gassensoren', len(sensor_info['mq_sensoren'])])
    csv_data.append(['Grunddaten', 'Umweltsensoren', len(sensor_info['umwelt_sensoren'])])
    csv_data.append(['Grunddaten', 'Zeitfelder', len(sensor_info['zeit_spalten'])])
    
    # Spalteninfo
    for i, col in enumerate(df.columns, 1):
        dtype = str(df[col].dtype)
        null_count = df[col].isnull().sum()
        unique_count = df[col].nunique()
        csv_data.append(['Spalten', f'{i:02d}_{col}', f'{dtype}|{null_count}_NULL|{unique_count}_eindeutig'])
    
    # MQ-Sensor Statistiken
    if sensor_info['mq_sensoren']:
        mq_stats = df[sensor_info['mq_sensoren']].describe()
        for stat in mq_stats.index:
            for sensor in sensor_info['mq_sensoren']:
                sensor_stat_value = round(mq_stats.loc[stat, sensor], DECIMAL_PLACES)
                csv_data.append(['MQ_Statistik', f'{sensor}_{stat}', sensor_stat_value])
        
        # Korrelationen
        if len(sensor_info['mq_sensoren']) > 1:
            korr_matrix = df[sensor_info['mq_sensoren']].corr()
            for i in range(len(korr_matrix.columns)):
                for j in range(i+1, len(korr_matrix.columns)):
                    corr_val = korr_matrix.iloc[i, j]
                    sensor1 = korr_matrix.columns[i]
                    sensor2 = korr_matrix.columns[j]
                    csv_data.append(['Korrelation', f'{sensor1}_vs_{sensor2}', round(corr_val, 3)])
    
    # Datenqualität
    total_cells = df.size
    null_cells = df.isnull().sum().sum()
    completeness = ((total_cells - null_cells) / total_cells) * 100
    csv_data.append(['Qualität', 'Vollständigkeit_Prozent', round(completeness, 1)])
    csv_data.append(['Qualität', 'Fehlende_Werte', null_cells])
    csv_data.append(['Qualität', 'Gesamt_Zellen', total_cells])
    
    # CSV speichern
    import csv
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(csv_data)
    
    print(f"\n✅ Detaillierter Report erstellt:")
    print(f"   📄 TXT: {info_filename}")
    print(f"   📊 CSV: {csv_filename}")
    return info_filename, csv_filename

def main():
    """
    Hauptfunktion für die Gassensor-Datenanalyse
    """
    print("🚀 GASSENSOR CSV ANALYSER")
    print("=" * 50)
    
    import sys
    
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    else:
        # CSV-Ordner aus Konfiguration verwenden
        csv_ordner = DEFAULT_CSV_FOLDER
        
        # Verfügbare CSV-Dateien im definierten Ordner anzeigen
        try:
            csv_files = [f for f in os.listdir(csv_ordner) if f.lower().endswith('.csv')]
        except FileNotFoundError:
            print(f"❌ Ordner nicht gefunden: {csv_ordner}")
            return
        
        # Spezielle Suche nach LOG-Dateien
        log_files = [f for f in csv_files if 'log' in f.lower() or 'home-' in f.lower()]
        
        if csv_files:
            print(f"📂 CSV-Dateien in: {csv_ordner}")
            if log_files:
                print("   🏠 LOG-Dateien gefunden:")
                for i, f in enumerate(log_files, 1):
                    file_path = os.path.join(csv_ordner, f)
                    file_size = os.path.getsize(file_path) / FILE_SIZE_UNIT  # KB
                    print(f"     {i}. {f} ({file_size:.0f} KB)")
                print("   📊 Andere CSV-Dateien:")
                other_files = [f for f in csv_files if f not in log_files]
                for i, f in enumerate(other_files, len(log_files) + 1):
                    file_path = os.path.join(csv_ordner, f)
                    file_size = os.path.getsize(file_path) / FILE_SIZE_UNIT  # KB
                    print(f"     {i}. {f} ({file_size:.0f} KB)")
                
                # Alle Dateien zusammenfassen für Auswahl
                all_files = log_files + other_files
            else:
                all_files = csv_files
                for i, f in enumerate(csv_files, 1):
                    file_path = os.path.join(csv_ordner, f)
                    file_size = os.path.getsize(file_path) / FILE_SIZE_UNIT  # KB
                    print(f"  {i}. {f} ({file_size:.0f} KB)")
            
            print(f"\n  {len(all_files) + 1}. 📝 Eigenen Dateinamen eingeben")
            
            user_input = input("\nWähle eine Option (Nummer) oder gib direkt einen Dateinamen ein: ").strip()
            
            # Prüfen ob es eine Nummer ist
            try:
                choice = int(user_input) - 1
                
                if choice == len(all_files):
                    # Eigenen Dateinamen eingeben
                    csv_file = input("📝 Dateiname eingeben (z.B. Home-LOG2025-07-12-2258.csv): ").strip()
                    
                    # .csv Endung automatisch hinzufügen falls vergessen
                    if not csv_file.lower().endswith('.csv'):
                        csv_file += '.csv'
                    
                    # Vollständigen Pfad erstellen
                    csv_file = os.path.join(csv_ordner, csv_file)
                    
                    if not os.path.exists(csv_file):
                        print(f"❌ Datei nicht gefunden: {csv_file}")
                        print("💡 Stelle sicher, dass die Datei im Ordner liegt:")
                        print(f"   {csv_ordner}")
                        return
                    print(f"✅ Eigene Datei gewählt: {os.path.basename(csv_file)}")
                elif 0 <= choice < len(all_files):
                    csv_file = os.path.join(csv_ordner, all_files[choice])
                    print(f"✅ Gewählte Datei: {all_files[choice]}")
                else:
                    print("❌ Ungültige Nummer!")
                    return
                    
            except ValueError:
                # Es ist keine Nummer, also direkt als Dateiname verwenden
                csv_file = user_input
                
                # .csv Endung automatisch hinzufügen falls vergessen
                if not csv_file.lower().endswith('.csv'):
                    csv_file += '.csv'
                
                # Vollständigen Pfad erstellen
                csv_file = os.path.join(csv_ordner, csv_file)
                
                if not os.path.exists(csv_file):
                    print(f"❌ Datei nicht gefunden: {csv_file}")
                    print("💡 Stelle sicher, dass die Datei im Ordner liegt:")
                    print(f"   {csv_ordner}")
                    print("📂 Verfügbare Dateien:")
                    for f in all_files:
                        print(f"   - {f}")
                    return
                print(f"✅ Datei direkt gewählt: {os.path.basename(csv_file)}")
        else:
            print(f"📂 Keine CSV-Dateien gefunden in: {csv_ordner}")
            csv_file = input("📝 CSV-Dateiname eingeben (z.B. Home-LOG2025-07-12-2258.csv): ").strip()
            
            # .csv Endung automatisch hinzufügen falls vergessen
            if not csv_file.lower().endswith('.csv'):
                csv_file += '.csv'
            
            # Vollständigen Pfad erstellen
            csv_file = os.path.join(csv_ordner, csv_file)
                
            if not os.path.exists(csv_file):
                print(f"❌ Datei nicht gefunden: {csv_file}")
                print(f"💡 Stelle sicher, dass die Datei im Ordner liegt:")
                print(f"   {csv_ordner}")
                return
    
    # Analyse durchführen
    df = parse_sensor_csv(csv_file)
    if df is None:
        return
    
    # Gassensor-spezifische Analyse
    sensor_info = analyse_gassensor_data(df, os.path.dirname(csv_file))
    
    # Detaillierter Report
    report_files = create_detailed_report(df, csv_file, sensor_info)
    
    print(f"\n🎯 ANALYSE ABGESCHLOSSEN!")
    print(f"📊 Analysierte Daten: {df.shape[0]:,} Messungen von {sensor_info['total_sensoren']} Sensoren")
    print(f"📁 Erstelle Dateien verfügbar für weitere Analysen")

if __name__ == "__main__":
    main()
