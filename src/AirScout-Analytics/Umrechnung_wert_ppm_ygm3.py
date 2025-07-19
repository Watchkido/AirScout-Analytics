"""
Sensorwerte-Umrechnungsmodul für Gassensoren
============================================

Funktionen zur Umrechnung von rohen Sensorwerten in ppm und µg/m³
Liest CSV-Dateien aus data/roh und speichert umgerechnete Werte in
data/bearbeitet

Umrechnungsformel:
- ppm = A * (Rs/R0)^B * Kalibrierungsfaktor
- µg/m³ = ppm × (Molare Masse / CONFIG.MOLAR_VOLUME_STP) × CONFIG.PPM_TO_UGM3_FACTOR

Kalibriert für realistische Werte basierend auf Waldstation Pfälzerwald:
NO2: 1-5 µg/m³, CnHm: 9-20 µg/m³
"""
import pandas as pd
from pathlib import Path
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

# Lade alle Konstanten aus Config
SENSOR_MODELS = CONFIG.SENSOR_KALIBRIERUNG['SENSOR_MODELS']
MOLAR_MASSES = CONFIG.MOLAR_MASSES
AQI_BREAKPOINTS = CONFIG.AQI_BREAKPOINTS
AQI_CATEGORIES = CONFIG.AQI_CATEGORIES

# Umrechnungskonstanten aus Config
MOLAR_VOLUME_STP = CONFIG.UMRECHNUNG_KONSTANTEN['MOLAR_VOLUME_STP']
PPM_TO_UGM3_FACTOR = CONFIG.UMRECHNUNG_KONSTANTEN['PPM_TO_UGM3_FACTOR']
MAX_REALISTIC_PPM = CONFIG.UMRECHNUNG_KONSTANTEN['MAX_REALISTIC_PPM']
MAX_REALISTIC_UGM3 = CONFIG.UMRECHNUNG_KONSTANTEN['MAX_REALISTIC_UGM3']
MIN_VALID_RATIO = CONFIG.UMRECHNUNG_KONSTANTEN['MIN_VALID_RATIO']
MAX_VALID_RATIO = CONFIG.UMRECHNUNG_KONSTANTEN['MAX_VALID_RATIO']
DECIMAL_PLACES = CONFIG.UMRECHNUNG_KONSTANTEN['DECIMAL_PLACES']
OUTPUT_SUFFIX = CONFIG.UMRECHNUNG_KONSTANTEN['OUTPUT_SUFFIX']


def convert_to_ppm(sensor_value, sensor_name):
    """
    Konvertiert rohen Sensorwert zu ppm
    
    Args:
        sensor_value: Roher Sensorwert
        sensor_name: Name des Sensors (z.B. 'MQ2')
    
    Returns:
        float: ppm-Wert oder 0.0 falls Umrechnung nicht möglich
    """
    # Prüfe auf ungültige Werte
    if pd.isna(sensor_value) or sensor_value <= 0:
        return 0.0
        
    R0 = R0_VALUES.get(sensor_name)
    sensor_data = SENSOR_MODELS.get(sensor_name)
    kalibrierung = KALIBRIERUNG_FAKTOREN.get(sensor_name, 1.0)
    
    if R0 is None or sensor_data is None:
        return 0.0
    
    A = sensor_data['A']
    B = sensor_data['B']
    
    if A == 0 or B == 0:
        return 0.0
    
    try:
        Rs = float(sensor_value)
        ratio = Rs / R0
        
        # Verhindere negative oder extreme Werte
        if ratio <= MIN_VALID_RATIO or ratio > MAX_VALID_RATIO:
            return 0.0
            
        ppm_value = A * (ratio ** B) * kalibrierung
        
        # Stelle sicher, dass der Wert positiv und realistisch ist
        if ppm_value < 0 or ppm_value > MAX_REALISTIC_PPM:
            return 0.0
        
        # Runde auf konfigurierte Dezimalstellen für saubere Ausgabe
        return round(ppm_value, DECIMAL_PLACES)
        
    except (ValueError, OverflowError, ZeroDivisionError):
        return 0.0


def convert_to_ygm3(ppm_value, sensor_name):
    """
    Konvertiert ppm zu µg/m³ (als ygm3 bezeichnet)
    
    Args:
        ppm_value: ppm-Wert
        sensor_name: Name des Sensors
    
    Returns:
        float: µg/m³-Wert oder 0.0 falls Umrechnung nicht möglich
    """
    M = MOLAR_MASSES.get(sensor_name)
    if M is None or pd.isna(ppm_value) or ppm_value <= 0:
        return 0.0
    
    try:
        ygm3_value = ppm_value * (M / MOLAR_VOLUME_STP) * PPM_TO_UGM3_FACTOR
        
        # Stelle sicher, dass der Wert realistisch ist
        if ygm3_value < 0 or ygm3_value > MAX_REALISTIC_UGM3:
            return 0.0
        
        # Runde auf konfigurierte Dezimalstellen
        return round(ygm3_value, DECIMAL_PLACES)
        
    except (ValueError, OverflowError):
        return 0.0


def calculate_aqi(concentration, pollutant):
    """
    Berechnet AQI-Wert basierend auf Schadstoffkonzentration
    
    Args:
        concentration: Konzentration in µg/m³
        pollutant: Schadstoff ('PM2.5', 'PM10', 'NO2', 'CO', 'O3')
    
    Returns:
        tuple: (AQI-Wert, Kategorie, Farbe, Beschreibung)
    """
    if concentration <= 0 or pollutant not in AQI_BREAKPOINTS:
        return (0, 'Unknown', 'Grau', 'Keine gültigen Daten')
    
    breakpoints = AQI_BREAKPOINTS[pollutant]
    
    # Finde passenden Breakpoint
    for bp_low, bp_high, aqi_low, aqi_high in breakpoints:
        if bp_low <= concentration <= bp_high:
            # Lineare Interpolation
            aqi = ((aqi_high - aqi_low) / (bp_high - bp_low)) * \
                  (concentration - bp_low) + aqi_low
            aqi = round(aqi)
            
            # Finde Kategorie
            for (cat_low, cat_high), (name, color, desc) in AQI_CATEGORIES.items():
                if cat_low <= aqi <= cat_high:
                    return (aqi, name, color, desc)
    
    # Wenn über allen Breakpoints
    return (500, 'Hazardous', 'Kastanienbraun', 'Extrem gefährlich')


def map_sensor_to_pollutant(sensor_name):
    """
    Ordnet Sensor-Namen den AQI-Schadstoffen zu
    
    Args:
        sensor_name: Name des Sensors (z.B. 'MQ135')
    
    Returns:
        str: AQI-Schadstoff oder None
    """
    return CONFIG.SENSOR_TO_POLLUTANT_MAPPING.get(sensor_name)


def process_csv_file(input_file, output_file):
    """
    Verarbeitet eine CSV-Datei und fügt ppm und µg/m³ Spalten hinzu
    
    Args:
        input_file: Pfad zur Eingabe-CSV-Datei
        output_file: Pfad zur Ausgabe-CSV-Datei
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
            ppm_col = f'{sensor}_ppm'
            ygm3_col = f'{sensor}_ygm3'
            aqi_col = f'{sensor}_aqi'
            aqi_category_col = f'{sensor}_aqi_category'
            
            print(f"Verarbeite Sensor {sensor}...")
            
            # ppm-Werte berechnen
            df[ppm_col] = df[sensor].apply(
                lambda x: convert_to_ppm(x, sensor)
            )
            
            # µg/m³-Werte berechnen (als ygm3 bezeichnet)
            df[ygm3_col] = df[ppm_col].apply(
                lambda x: convert_to_ygm3(x, sensor)
            )
            
            # AQI-Werte berechnen (falls Sensor unterstützt wird)
            pollutant = map_sensor_to_pollutant(sensor)
            if pollutant:
                aqi_data = df[ygm3_col].apply(
                    lambda x: calculate_aqi(x, pollutant)
                )
                df[aqi_col] = [aqi[0] for aqi in aqi_data]
                df[aqi_category_col] = [aqi[1] for aqi in aqi_data]
                print(f"  → AQI-Werte für {pollutant} berechnet")
            else:
                df[aqi_col] = 0
                df[aqi_category_col] = 'N/A'
        
        # Stelle sicher, dass der Ausgabeordner existiert
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Datei speichern
        df.to_csv(output_file, index=False)
        print(f"Datei gespeichert: {output_file}")
        
        # AQI-Zusammenfassung generieren und anzeigen
        aqi_summary = generate_aqi_summary(df)
        if aqi_summary:
            print_aqi_summary(aqi_summary, output_file.name)
        
        return True
        
    except Exception as e:
        print(f"Fehler beim Verarbeiten von {input_file}: {str(e)}")
        return False


def process_all_csv_files():
    """
    Verarbeitet alle CSV-Dateien im data/roh Ordner
    """
    # Stelle sicher, dass die Ordner existieren
    DATA_ROH_PATH.mkdir(parents=True, exist_ok=True)
    DATA_BEARBEITET_PATH.mkdir(parents=True, exist_ok=True)
    
    # Finde alle CSV-Dateien im roh-Ordner
    csv_files = (list(DATA_ROH_PATH.glob("*.csv")) +
                 list(DATA_ROH_PATH.glob("*.CSV")))
    
    if not csv_files:
        print(f"Keine CSV-Dateien in {DATA_ROH_PATH} gefunden!")
        return
    
    print(f"Gefundene CSV-Dateien: {len(csv_files)}")
    
    successful = 0
    failed = 0
    
    for csv_file in csv_files:
        # Erstelle Ausgabe-Dateinamen
        output_name = f"{csv_file.stem}{OUTPUT_SUFFIX}.csv"
        output_file = DATA_BEARBEITET_PATH / output_name
        
        # Verarbeite die Datei
        if process_csv_file(csv_file, output_file):
            successful += 1
        else:
            failed += 1
    
    print("\nVerarbeitung abgeschlossen:")
    print(f"Erfolgreich: {successful}")
    print(f"Fehlgeschlagen: {failed}")


def process_single_file(filename):
    """
    Verarbeitet eine einzelne CSV-Datei aus dem data/roh Ordner
    
    Args:
        filename: Name der CSV-Datei (z.B. 'Home-LOG2025-07-12-2258.csv')
    
    Returns:
        bool: True falls erfolgreich, False bei Fehler
    """
    input_file = DATA_ROH_PATH / filename
    
    if not input_file.exists():
        print(f"Datei nicht gefunden: {input_file}")
        return False
    
    # Erstelle Ausgabe-Dateinamen
    output_name = f"{input_file.stem}{OUTPUT_SUFFIX}.csv"
    output_file = DATA_BEARBEITET_PATH / output_name
    
    return process_csv_file(input_file, output_file)


def show_expected_values():
    """
    Zeigt erwartete Werte für die Eichfahrt basierend auf Waldstation
    """
    print("\n" + "="*70)
    print("ERWARTETE WERTE FÜR EICHFAHRT - WALDSTATION REFERENZ")
    print("="*70)
    print("Basierend auf Waldstation Pfälzerwald-Hortenkopf (15.07.2025)")
    print("\nREFERENZWERTE der Waldstation (µg/m³):")
    print("  NO2:          1-3     (MQ135: sehr saubere Waldluft)")
    print("  CnHm:         9-17    (MQ2/4/5/6: Kohlenwasserstoffe)")
    print("  CO:          <0.5     (MQ7/9: praktisch null)")
    print("  SO2:         ~1       (sehr niedrig)")
    print("  O3:          58-86    (Ozon, variiert stark tageszeitlich)")
    print("  PM10:        8-12     (Feinstaub)")
    print("  PM2.5:       5-6      (Ultrafeinstaub)")
    
    print("\nERWARTETE AQI-WERTE (Air Quality Index):")
    print("  NO2 (1-3 µg/m³):      AQI 0-50   (Good/Grün)")
    print("  CO (<0.5 µg/m³):      AQI 0-50   (Good/Grün)")
    print("  O3 (58-86 µg/m³):     AQI 0-50   (Good/Grün)")
    print("  PM10 (8-12 µg/m³):    AQI 0-50   (Good/Grün)")
    print("  PM2.5 (5-6 µg/m³):    AQI 0-50   (Good/Grün)")
    
    print("\nIhre kalibrierten Zielbereiche (µg/m³):")
    zielwerte = CONFIG.SENSOR_KALIBRIERUNG['ZIELWERTE_UGM3']
    for gas, (min_val, max_val) in zielwerte.items():
        sensor_mapping = {
            'NO2': 'MQ135',
            'CO': 'MQ7/MQ9',
            'CnHm': 'MQ2/MQ4/MQ5/MQ6',
            'Alkohol': 'MQ3',
            'H2': 'MQ8'
        }
        sensor = sensor_mapping.get(gas, gas)
        
        # Berechne erwarteten AQI für Zielbereich
        if gas == 'NO2':
            aqi_min = calculate_aqi(min_val, 'NO2')[0]
            aqi_max = calculate_aqi(max_val, 'NO2')[0]
            aqi_info = f"AQI {aqi_min}-{aqi_max}"
        elif gas == 'CO':
            aqi_min = calculate_aqi(min_val, 'CO')[0]
            aqi_max = calculate_aqi(max_val, 'CO')[0]
            aqi_info = f"AQI {aqi_min}-{aqi_max}"
        else:
            aqi_info = "AQI N/A"
        
        print(f"  {gas:8} ({sensor:12}): {min_val:4.1f}-{max_val:2.0f} µg/m³ "
              f"({aqi_info})")
    
    print("\nAQI-KATEGORIEN:")
    print("  0-50:   Good (Grün)           - Luftqualität zufriedenstellend")
    print("  51-100: Moderate (Gelb)       - Luftqualität akzeptabel")
    print("  101-150: Unhealthy for Sensitive (Orange) - Empfindliche Probleme")
    print("  151-200: Unhealthy (Rot)      - Jeder kann Probleme haben")
    print("  201-300: Very Unhealthy (Lila) - Gesundheitswarnung")
    print("  301-500: Hazardous (Kastanie) - Notfall-Bedingungen")
    
    print("\nTipps für die Eichfahrt zur Waldstation:")
    print("  [+] Fahren Sie früh morgens (5-8 Uhr, weniger Verkehr)")
    print("  [+] Messen Sie 10 Min vor Waldgebiet (Baseline)")
    print("  [+] Messen Sie im Wald (saubere Referenz)")
    print("  [+] Dokumentieren Sie Wetter und Windrichtung")
    print("  [+] Notieren Sie Verkehrslage und Uhrzeit")
    print("  [+] Vergleichen Sie mit Echtzeit-Stationsdaten")
    print("  [+] Erwarten Sie NO2: 1-3 µg/m³, CnHm: 9-17 µg/m³")
    print("  [+] Alle AQI-Werte sollten im 'Good' Bereich (0-50) liegen")
    print("="*70)


def generate_aqi_summary(df):
    """
    Generiert eine AQI-Zusammenfassung für einen DataFrame
    
    Args:
        df: DataFrame mit AQI-Spalten
    
    Returns:
        dict: AQI-Zusammenfassung
    """
    summary = {}
    aqi_sensors = CONFIG.AQI_SUPPORTED_SENSORS  # Sensoren mit AQI-Unterstützung
    
    for sensor in aqi_sensors:
        aqi_col = f'{sensor}_aqi'
        category_col = f'{sensor}_aqi_category'
        ygm3_col = f'{sensor}_ygm3'
        
        if aqi_col in df.columns:
            aqi_values = df[aqi_col].replace(0, pd.NA).dropna()
            ygm3_values = df[ygm3_col].replace(0.0, pd.NA).dropna()
            categories = df[category_col][df[category_col] != 'N/A']
            
            if len(aqi_values) > 0:
                pollutant = map_sensor_to_pollutant(sensor)
                summary[sensor] = {
                    'pollutant': pollutant,
                    'aqi_min': int(aqi_values.min()),
                    'aqi_max': int(aqi_values.max()),
                    'aqi_mean': round(aqi_values.mean(), 1),
                    'concentration_min': round(ygm3_values.min(), 2),
                    'concentration_max': round(ygm3_values.max(), 2),
                    'concentration_mean': round(ygm3_values.mean(), 2),
                    'worst_category': categories.mode().iloc[0] if len(categories) > 0 else 'N/A',
                    'measurements': len(aqi_values)
                }
    
    return summary


def print_aqi_summary(summary, filename):
    """
    Druckt eine formatierte AQI-Zusammenfassung
    """
    print(f"\n{'='*60}")
    print(f"AQI-ZUSAMMENFASSUNG: {filename}")
    print(f"{'='*60}")
    
    if not summary:
        print("Keine AQI-Daten verfügbar.")
        return
    
    for sensor, data in summary.items():
        pollutant = data['pollutant']
        print(f"\n{sensor} ({pollutant}):")
        print(f"  Konzentration: {data['concentration_min']}-{data['concentration_max']} µg/m³ "
              f"(Ø {data['concentration_mean']})")
        print(f"  AQI-Bereich:   {data['aqi_min']}-{data['aqi_max']} "
              f"(Ø {data['aqi_mean']})")
        print(f"  Schlechteste Kategorie: {data['worst_category']}")
        print(f"  Messwerte: {data['measurements']}")
        
        # Bewertung
        if data['aqi_max'] <= 50:
            bewertung = "[+] AUSGEZEICHNET (Good)"
        elif data['aqi_max'] <= 100:
            bewertung = "[!] AKZEPTABEL (Moderate)"
        elif data['aqi_max'] <= 150:
            bewertung = "[!] BEDENKLICH (Unhealthy for Sensitive)"
        else:
            bewertung = "[X] PROBLEMATISCH (Unhealthy+)"
        
        print(f"  Bewertung: {bewertung}")
    
    print(f"\n{'='*60}")


if __name__ == "__main__":
    # Zeige erwartete Werte vor der Verarbeitung
    show_expected_values()
    
    # Verarbeite alle CSV-Dateien wenn das Script direkt ausgeführt wird
    process_all_csv_files()