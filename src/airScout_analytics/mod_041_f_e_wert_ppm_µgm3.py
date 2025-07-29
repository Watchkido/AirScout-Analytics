"""
Sensorwerte-Umrechnungsmodul für Gassensoren
============================================

Funktionen zur Umrechnung von rohen Sensorwerten in ppm und µg/m³.
Liest CSV-Dateien aus data/roh und speichert umgerechnete Werte in data/bearbeitet.

Umrechnungsformel:
- ppm = A * (Rs/R0)^B * Kalibrierungsfaktor
- µg/m³ = ppm × (Molare Masse / 24.45) × 1000

Kalibriert für realistische Werte basierend auf Waldstation Pfälzerwald:
NO2: 1-5 µg/m³, CnHm: 9-20 µg/m³
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=Warning)
try:
    from config import CONFIG
except ModuleNotFoundError:
    try:
        from config import CONFIG
    except ModuleNotFoundError:
        import sys
        import os
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
        from config import CONFIG

# Projektpfade definieren
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_ROH_PATH = PROJECT_ROOT / "data" / "bearbeitet1"
DATA_BEARBEITET_PATH = PROJECT_ROOT / "data" / "bearbeitet2"

# R0-Werte bei sauberer Luft (kalibriert für realistische Werte)
# Basierend auf Waldstation Pfälzerwald: NO2=1-5 µg/m³, CnHm=9-20 µg/m³
R0_VALUES = CONFIG.SENSOR_KALIBRIERUNG['R0_VALUES']

# Kalibrierungsfaktoren für realistische ppm-Werte
KALIBRIERUNG_FAKTOREN = CONFIG.SENSOR_KALIBRIERUNG['KALIBRIERUNG_FAKTOREN']

# Sensormodelle: A & B für Formel ppm = A * (Rs/R0)^B
# Angepasst für realistische Umgebungsmessungen
SENSOR_MODELS = {
    'MQ2':   {'A': 100.0, 'B': -1.5},    # LPG, Propan, Wasserstoff
    'MQ3':   {'A': 50.0, 'B': -1.3},     # Alkohol (meist sehr niedrig)
    'MQ4':   {'A': 80.0, 'B': -1.4},     # Methan
    'MQ5':   {'A': 90.0, 'B': -1.6},     # LPG
    'MQ6':   {'A': 85.0, 'B': -1.5},     # LPG, Butan
    'MQ7':   {'A': 60.0, 'B': -1.2},     # CO (sehr niedrige Werte)
    'MQ8':   {'A': 70.0, 'B': -1.4},     # Wasserstoff
    'MQ9':   {'A': 75.0, 'B': -1.3},     # CO/Brennbare Gase
    'MQ135': {'A': 40.0, 'B': -1.1}      # NO₂, NH₃ (niedrige Umgebungswerte)
}

# Molare Massen (g/mol) für Gase mit ppm → µg/m³ Umrechnung
MOLAR_MASSES = {
    'MQ135': 46.0,  # NO₂
    'MQ7':   28.0,  # CO
    'MQ2':   44.0,  # LPG (Propan C3H8)
    'MQ3':   46.0,  # Ethanol C2H5OH
    'MQ4':   16.0,  # Methan CH4
    'MQ5':   44.0,  # LPG (Propan)
    'MQ6':   44.0,  # LPG (Propan)
    'MQ8':   2.0,   # Wasserstoff H2
    'MQ9':   28.0   # CO/Brennbare Gase
}

def convert_to_ppm(sensor_value: float, sensor_name: str) -> float:
    """
    Konvertiert rohen Sensorwert zu ppm.

    :param sensor_value: Roher Sensorwert
    :type sensor_value: float
    :param sensor_name: Name des Sensors (z.B. 'MQ2')
    :type sensor_name: str
    :returns: ppm-Wert oder np.nan falls Umrechnung nicht möglich
    :rtype: float
    """
    # Prüfe auf ungültige Werte
    if pd.isna(sensor_value) or sensor_value <= 0:
        return np.nan
        
    R0 = R0_VALUES.get(sensor_name)
    sensor_data = SENSOR_MODELS.get(sensor_name)
    kalibrierung = KALIBRIERUNG_FAKTOREN.get(sensor_name, 1.0)
    
    if R0 is None or sensor_data is None:
        return np.nan
    
    A = sensor_data['A']
    B = sensor_data['B']
    
    if A == 0 or B == 0:
        return np.nan
    
    Rs = sensor_value
    ratio = Rs / R0
    ppm_value = A * (ratio ** B) * kalibrierung
    
    # Runde auf 2 Dezimalstellen für saubere Ausgabe
    return round(ppm_value, 2)


def convert_to_ugm3(ppm_value: float, sensor_name: str) -> float:
    """
    Konvertiert ppm zu µg/m³.

    :param ppm_value: ppm-Wert
    :type ppm_value: float
    :param sensor_name: Name des Sensors
    :type sensor_name: str
    :returns: µg/m³-Wert oder np.nan falls Umrechnung nicht möglich
    :rtype: float
    """
    M = MOLAR_MASSES.get(sensor_name)
    if M is None or np.isnan(ppm_value):
        return np.nan
    
    ugm3_value = ppm_value * (M / 24.45) * 1000
    
    # Runde auf 2 Dezimalstellen
    return round(ugm3_value, 2)


def process_csv_file(input_file: Path, output_file: Path) -> bool:
    """
    Verarbeitet eine CSV-Datei und fügt ppm- und µg/m³-Spalten hinzu.

    :param input_file: Pfad zur Eingabe-CSV-Datei
    :type input_file: Path
    :param output_file: Pfad zur Ausgabe-CSV-Datei
    :type output_file: Path
    :returns: True bei Erfolg, False bei Fehler
    :rtype: bool
    """
    try:
        # CSV-Datei einlesen
        print(f"Lade Datei: {input_file}")
        df = pd.read_csv(input_file, comment='#')
        
        # Prüfe welche MQ-Sensoren in der Datei vorhanden sind
        available_sensors = [col for col in df.columns if col in R0_VALUES]
        print(f"Gefundene Sensoren: {available_sensors}")
        
        if not available_sensors:
            print("Keine MQ-Sensoren in der Datei gefunden!")
            return False
        
        # Neue Spalten für jeden Sensor erzeugen
        for sensor in available_sensors:
            ppm_col = f"{sensor}_ppm"
            ugm3_col = f"{sensor}_ugm3"
            
            print(f"Verarbeite Sensor {sensor}...")
            
            # ppm-Werte berechnen
            df[ppm_col] = df[sensor].apply(
                lambda x: convert_to_ppm(x, sensor)
            )
            
            # µg/m³-Werte berechnen
            df[ugm3_col] = df[ppm_col].apply(
                lambda x: convert_to_ugm3(x, sensor)
            )
        
        # Stelle sicher, dass der Ausgabeordner existiert
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Datei speichern
        df.to_csv(output_file, index=False)
        print(f"Datei gespeichert: {output_file}")
        return True
        
    except Exception as e:
        print(f"Fehler beim Verarbeiten von {input_file}: {str(e)}")
        return False


def process_all_csv_files() -> None:
    """
    Verarbeitet alle CSV-Dateien im data/roh-Ordner.
    """
    # Stelle sicher, dass die Ordner existieren
    DATA_ROH_PATH.mkdir(parents=True, exist_ok=True)
    DATA_BEARBEITET_PATH.mkdir(parents=True, exist_ok=True)
    
    # Finde alle CSV-Dateien im roh-Ordner
    csv_files = list(DATA_ROH_PATH.glob("*.csv")) + list(DATA_ROH_PATH.glob("*.CSV"))
    
    if not csv_files:
        print(f"Keine CSV-Dateien in {DATA_ROH_PATH} gefunden!")
        return
    
    print(f"Gefundene CSV-Dateien: {len(csv_files)}")
    
    successful = 0
    failed = 0
    
    for csv_file in csv_files:
        # Erstelle Ausgabe-Dateinamen
        output_name = f"{csv_file.stem}_umgerechnet.csv"
        output_file = DATA_BEARBEITET_PATH / output_name
        
        # Verarbeite die Datei
        if process_csv_file(csv_file, output_file):
            successful += 1
        else:
            failed += 1
    
    print("\nVerarbeitung abgeschlossen:")
    print(f"Erfolgreich: {successful}")
    print(f"Fehlgeschlagen: {failed}")


def process_single_file(filename: str) -> bool:
    """
    Verarbeitet eine einzelne CSV-Datei aus dem data/roh-Ordner.

    :param filename: Name der CSV-Datei (z.B. 'Home-LOG2025-07-12-2258.csv')
    :type filename: str
    :returns: True falls erfolgreich, False bei Fehler
    :rtype: bool
    """
    input_file = DATA_ROH_PATH / filename
    
    if not input_file.exists():
        print(f"Datei nicht gefunden: {input_file}")
        return False
    
    # Erstelle Ausgabe-Dateinamen
    output_name = f"{input_file.stem}_umgerechnet.csv"
    output_file = DATA_BEARBEITET_PATH / output_name
    
    return process_csv_file(input_file, output_file)


def show_expected_values() -> None:
    """
    Zeigt erwartete Werte für die Eichfahrt basierend auf Waldstation.
    """
    print("\n" + "=" * 60)
    print("ERWARTETE WERTE FÜR EICHFAHRT - WALDSTATION REFERENZ")
    print("=" * 60)
    print("Basierend auf Waldstation Pfälzerwald-Hortenkopf (15.07.2025)")
    print("\nReferenzwerte (µg/m³):")
    print("  NO2 (MQ135):  1-5    (sehr niedrig, saubere Waldluft)")
    print("  CnHm (MQ2-6): 9-20   (Kohlenwasserstoffe)")
    print("  CO (MQ7,9):   <2     (praktisch null)")
    print("  SO2:          ~1     (sehr niedrig)")
    print("  O3:           58-86  (Ozon, variiert stark)")
    
    print("\nIhre aktuellen kalibrierten Bereiche:")
    zielwerte = CONFIG.SENSOR_KALIBRIERUNG['ZIELWERTE_UGM3']
    for gas, (min_val, max_val) in zielwerte.items():
        print(f"  {gas:8}: {min_val:3}-{max_val:2} µg/m³")
    
    print("\nTipps für die Eichfahrt:")
    print("  - Fahren Sie früh morgens (weniger Verkehr)")
    print("  - Messen Sie vor/nach Waldgebiet")
    print("  - Dokumentieren Sie Wetter und Verkehrslage")
    print("  - Vergleichen Sie mit offiziellen Stationsdaten")
    print("=" * 60)


def main() -> None:
    """
    Pipeline-kompatibler Einstiegspunkt: Führt process_all_csv_files() aus.
    """
    process_all_csv_files()


if __name__ == "__main__":
    # Zeige erwartete Werte vor der Verarbeitung
    show_expected_values()
    
    # Verarbeite alle CSV-Dateien wenn das Script direkt ausgeführt wird
    process_all_csv_files()