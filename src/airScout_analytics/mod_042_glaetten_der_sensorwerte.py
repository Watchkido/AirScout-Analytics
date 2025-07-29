import os
from config import CONFIG
import context

EMA_SPAN = CONFIG.EMA_ANALYSE.get('EMA_SPAN', 5)
ZSCORE_THRESHOLD = CONFIG.EMA_ANALYSE.get('ZSCORE_THRESHOLD', 3)
GAS_THRESHOLD_MULTIPLIER = CONFIG.EMA_ANALYSE.get('GAS_THRESHOLD_MULTIPLIER', 1.5)
GAS_EVENT_WINDOW = CONFIG.EMA_ANALYSE.get('GAS_EVENT_WINDOW', 5)
ANOMALY_CONTAMINATION = CONFIG.EMA_ANALYSE.get('ANOMALY_CONTAMINATION', 0.05)
ML_RANDOM_STATE = CONFIG.EMA_ANALYSE.get('ML_RANDOM_STATE', 42)
ML_N_ESTIMATORS = CONFIG.EMA_ANALYSE.get('ML_N_ESTIMATORS', 100)

# Hilfsfunktion zur Sensorerkennung
def identify_sensor_columns(df):
    """
    Identifiziert Sensorspalten im DataFrame.
    Gibt ein Dictionary mit 'all_sensors', 'mq_sensors' und 'environmental' zurück.
    """
    # Die gewünschten Sensorspalten
    all_sensors = [
        "Temperature_DHT_C", "Humidity_RH", "Light_Level", "Light_Percent",
        "MQ2", "MQ3", "MQ4", "MQ5", "MQ6", "MQ7", "MQ8", "MQ9", "MQ135",
        "Mic1", "Mic2"
    ]
    mq_sensors = [s for s in all_sensors if s.startswith("MQ") and s in df.columns]
    environmental = [s for s in ["Temperature_DHT_C", "Humidity_RH", "Light_Level", "Light_Percent"] if s in df.columns]
    return {
        "all_sensors": [s for s in all_sensors if s in df.columns],
        "mq_sensors": mq_sensors,
        "environmental": environmental
    }

import pandas as pd
import numpy as np
from pathlib import Path

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

import sys
import io
from config import CONFIG





OUTPUT_SUFFIX = CONFIG.EMA_ANALYSE['OUTPUT_SUFFIX']
def get_info_txt_path(filename_ohne_ext: str) -> str:
    """
    Gibt den Pfad zur Info-Textdatei für die aktuelle Session zurück.
    :param filename_ohne_ext: Dateiname ohne Erweiterung
    :type filename_ohne_ext: str
    :returns: Pfad zur Info-Textdatei
    :rtype: str
    :example:
        >>> get_info_txt_path('Home-LOG2025-07-12-2258_ema')
        'data/ergebnisse/Home-LOG2025-07-12-2258_ema/info.txt'
    """
    # IT-Witz: Wer Info.txt nicht findet, hat vermutlich die Doku gelöscht!
    print(f"[DEBUG] get_info_txt_path: filename_ohne_ext={filename_ohne_ext} (aus context)")
    return f"data/ergebnisse/{filename_ohne_ext}/{filename_ohne_ext}_info.txt"
def main() -> None:
    """
    Pipeline-kompatibler Einstiegspunkt: Führt process_all_csv_files() aus.
    """
    process_all_csv_files()


"""
Erweiterte Sensorwerte-Analyse mit EMA, Z-Score und Anomalieerkennung
==================================================================

Features:
- Exponential Moving Average (EMA) für Sensordaten
- Z-Score-Analyse für statistische Ausreißer
- Gas-Ereignis-Warnungen mit Moving Average + Thresholding
- ML-Anomalieerkennung mit Isolation Forest
- Speichert Ergebnisse als "_ema.csv"
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path
import re
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import warnings
import sys
import io
from config import CONFIG
import context


# Projektpfade definieren
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_ROH_PATH = PROJECT_ROOT / "data" / "bearbeitet2"
DATA_BEARBEITET_PATH = PROJECT_ROOT / "data" / "bearbeitet3"
ERGEBNISSE_PATH = PROJECT_ROOT / "data" / "ergebnisse"


def apply_ema_smoothing(df, sensor_groups):
    """
    Wendet Exponential Moving Average auf alle Sensorspalten an
    (bestimmte Spalten wie GPS, Radiation_CPS, *_zscore, *_outlier etc. werden explizit ausgeschlossen)
    """
    df_ema = df.copy()
    # Nur diese Spalten werden geglättet
    zu_glätten = [
        "Temperature_DHT_C", "Humidity_RH", "Light_Level", "Light_Percent",
        "MQ2", "MQ3", "MQ4", "MQ5", "MQ6", "MQ7", "MQ8", "MQ9", "MQ135",
        "Mic1", "Mic2"
    ]
    print(f"  → EMA-Glättung für diese Spalten: {zu_glätten}")
    for sensor in zu_glätten:
        if sensor in df.columns:
            ema_col = f"{sensor}_ema"
            df_ema[ema_col] = df[sensor].ewm(span=EMA_SPAN, adjust=False).mean()
            # Ersetze ursprüngliche Spalte mit EMA-Werten
            df_ema[sensor] = df_ema[ema_col]
            df_ema.drop(columns=[ema_col], inplace=True)
    return df_ema


def calculate_zscore_analysis(df, sensor_groups):
    """
    Berechnet Z-Score-Analyse für Sensordaten
    
    Args:
        df: DataFrame mit Sensordaten
        sensor_groups: Dictionary mit Sensorspalten
    
    Returns:
        DataFrame: DataFrame mit Z-Score-Spalten
    """
    df_zscore = df.copy()
    
    print(f"  → Z-Score-Analyse (Schwellenwert: {ZSCORE_THRESHOLD})")
    
    outlier_counts = {}
    
    for sensor in sensor_groups['all_sensors']:
        if sensor in df.columns:
            # Berechne Z-Score
            mean_val = df[sensor].mean()
            std_val = df[sensor].std()
            
            if std_val > 0:
                df_zscore[f"{sensor}_zscore"] = (df[sensor] - mean_val) / std_val
                
                # Markiere Ausreißer
                df_zscore[f"{sensor}_outlier"] = (
                    abs(df_zscore[f"{sensor}_zscore"]) > ZSCORE_THRESHOLD
                ).astype(int)
                
                outlier_counts[sensor] = df_zscore[f"{sensor}_outlier"].sum()
            else:
                df_zscore[f"{sensor}_zscore"] = 0
                df_zscore[f"{sensor}_outlier"] = 0
                outlier_counts[sensor] = 0
    
    # Ausgabe der Ausreißer-Statistik
    total_outliers = sum(outlier_counts.values())
    print(f"    Gefundene Ausreißer: {total_outliers}")
    
    return df_zscore


def detect_gas_events(df, sensor_groups):
    """
    Erkennt Gas-Ereignisse mit Moving Average + Thresholding
    
    Args:
        df: DataFrame mit Sensordaten
        sensor_groups: Dictionary mit Sensorspalten
    
    Returns:
        DataFrame: DataFrame mit Gas-Ereignis-Spalten
    """
    df_events = df.copy()
    
    print(f"  → Gas-Ereignis-Erkennung (Schwellenwert: {GAS_THRESHOLD_MULTIPLIER}x)")
    
    event_counts = {}
    
    for sensor in sensor_groups['mq_sensors']:
        if sensor in df.columns:
            # Berechne gleitenden Durchschnitt als Baseline
            baseline = df[sensor].rolling(window=GAS_EVENT_WINDOW, center=True).mean()
            
            # Berechne dynamischen Schwellenwert
            threshold = baseline * GAS_THRESHOLD_MULTIPLIER
            
            # Erkenne Ereignisse (Werte über Schwellenwert)
            df_events[f"{sensor}_event"] = (df[sensor] > threshold).astype(int)
            
            # Berechne Ereignis-Intensität (wie weit über Schwellenwert)
            df_events[f"{sensor}_intensity"] = np.maximum(
                0, (df[sensor] - threshold) / threshold
            )
            
            event_counts[sensor] = df_events[f"{sensor}_event"].sum()
    
    # Ausgabe der Ereignis-Statistik
    total_events = sum(event_counts.values())
    print(f"    Erkannte Gas-Ereignisse: {total_events}")
    
    return df_events


def detect_anomalies_ml(df, sensor_groups):
    """
    Erkennt Anomalien mit Isolation Forest ML-Algorithmus
    
    Args:
        df: DataFrame mit Sensordaten
        sensor_groups: Dictionary mit Sensorspalten
    
    Returns:
        DataFrame: DataFrame mit Anomalie-Spalten
    """
    df_anomaly = df.copy()
    
    print(f"  → ML-Anomalieerkennung (Isolation Forest)")
    
    # Bereite Daten für ML vor
    sensor_data = df[sensor_groups['all_sensors']].copy()
    
    # Entferne NaN-Werte
    sensor_data = sensor_data.fillna(sensor_data.mean())
    
    if len(sensor_data.columns) == 0:
        print("    Keine gültigen Sensordaten für ML gefunden")
        return df_anomaly
    
    try:
        # Standardisiere Daten
        scaler = StandardScaler()
        sensor_scaled = scaler.fit_transform(sensor_data)
        
        # Trainiere Isolation Forest
        iso_forest = IsolationForest(
            contamination=ANOMALY_CONTAMINATION,
            random_state=ML_RANDOM_STATE,
            n_estimators=ML_N_ESTIMATORS
        )
        
        # Erkenne Anomalien (-1 = Anomalie, 1 = Normal)
        anomaly_labels = iso_forest.fit_predict(sensor_scaled)
        anomaly_scores = iso_forest.score_samples(sensor_scaled)
        
        # Füge Ergebnisse zum DataFrame hinzu
        df_anomaly['ml_anomaly'] = (anomaly_labels == -1).astype(int)
        df_anomaly['ml_anomaly_score'] = anomaly_scores
        
        anomaly_count = df_anomaly['ml_anomaly'].sum()
        print(f"    ML-Anomalien erkannt: {anomaly_count} "
              f"({anomaly_count/len(df)*100:.1f}%)")
        
    except Exception as e:
        print(f"    ML-Fehler: {str(e)}")
        df_anomaly['ml_anomaly'] = 0
        df_anomaly['ml_anomaly_score'] = 0
    
    return df_anomaly


def process_csv_file(input_file, output_file):
    """
    Verarbeitet eine CSV-Datei mit vollständiger Sensoranalyse
    (bestimmte Spalten wie GPS, Radiation_CPS, *_zscore, *_outlier etc. werden explizit von der Rundung ausgenommen)
    """
    log_lines = []
    def log(msg):
        print(msg)
        log_lines.append(msg)
    try:
        log(f"Verarbeite: {input_file.name}")
        # 1. CSV laden (Standard-Import, da clean_csv_header nicht definiert)
        df = pd.read_csv(input_file)
        log(f"Spalten im DataFrame: {df.columns.tolist()}")
        if df.empty:
            log("  → Datei ist leer!")
            return False
        # 2. Sensorspalten identifizieren
        sensor_groups = identify_sensor_columns(df)
        log(f"Erkannte Sensorspalten: {sensor_groups.get('all_sensors', [])}")
        if not sensor_groups['all_sensors']:
            log("  → Keine Sensorspalten gefunden!")
            return False
        log(f"  → {len(sensor_groups['mq_sensors'])} MQ-Sensoren, {len(sensor_groups['environmental'])} Umweltsensoren")
        # 3. EMA-Glättung anwenden
        df_processed = apply_ema_smoothing(df, sensor_groups)
        # 4. Z-Score-Analyse
        df_processed = calculate_zscore_analysis(df_processed, sensor_groups)
        # 5. Gas-Ereignis-Erkennung
        df_processed = detect_gas_events(df_processed, sensor_groups)
        # 6. ML-Anomalieerkennung
        df_processed = detect_anomalies_ml(df_processed, sensor_groups)
        # 7. Stelle sicher, dass Ausgabeordner existiert
        output_file.parent.mkdir(parents=True, exist_ok=True)
        # 8. Bestimmte Spalten (GPS, Radiation_CPS, *_zscore, *_outlier etc.) von Glättung und Rundung ausnehmen
        ausnahme_spalten = [
            "GPS_Lat", "GPS_Lon", "GPS_Alt", "GPS_Speed", "GPS_Course", "GPS_Sats",
            "Radiation_CPS"
        ]
        ausnahme_spalten += [col for col in df_processed.columns if any(
            col.endswith(suffix) for suffix in ["_zscore", "_outlier", "_event", "_intensity", "_anomaly", "_score"]
        )]
        ausnahme_spalten = [col for col in ausnahme_spalten if col in df_processed.columns]
        original_werte = df_processed[ausnahme_spalten].copy() if ausnahme_spalten else None
        if ausnahme_spalten:
            df_gerundet = df_processed.round(3)
            for col in ausnahme_spalten:
                df_gerundet[col] = original_werte[col]
        else:
            df_gerundet = df_processed.round(3)
        # Speichere die finale Version in bearbeitet3
        try:
            df_gerundet.to_csv(output_file, index=False)
            log(f"  → Gespeichert in bearbeitet3: {output_file}")
            if not output_file.exists():
                log(f"  → Fehler: Datei wurde nicht gespeichert! Pfad: {output_file}")
        except Exception as e:
            log(f"  → Fehler beim Speichern in bearbeitet3: {e}")
        # 9. Zusammenfassung
        print_analysis_summary(df_processed, sensor_groups)
        log("Analyse abgeschlossen.")
        # Logdatei wird nicht mehr benötigt
        return True
    except Exception as e:
        log(f"  → Fehler bei {input_file.name}: {str(e)}")
        # Logdatei wird nicht mehr benötigt
        return False


def print_analysis_summary(df, sensor_groups):
    """
    Druckt eine Zusammenfassung der Analyse-Ergebnisse
    """
    print("  → ANALYSE-ZUSAMMENFASSUNG:")
    
    # Gesamtstatistiken
    total_outliers = sum(df[f"{s}_outlier"].sum() 
                        for s in sensor_groups['all_sensors'] 
                        if f"{s}_outlier" in df.columns)
    
    total_gas_events = sum(df[f"{s}_event"].sum() 
                          for s in sensor_groups['mq_sensors'] 
                          if f"{s}_event" in df.columns)
    
    ml_anomalies = df['ml_anomaly'].sum() if 'ml_anomaly' in df.columns else 0
    
    print(f"    Z-Score-Ausreißer: {total_outliers}")
    print(f"    Gas-Ereignisse: {total_gas_events}")
    print(f"    ML-Anomalien: {ml_anomalies}")
    print(f"    Neue Spalten: {len(df.columns) - len(sensor_groups['all_sensors'])}")



def process_all_csv_files():
    """
    Verarbeitet alle CSV-Dateien im data/roh Ordner und schreibt die Terminalausgabe in eine TXT-Datei im Ordner 'ergebnisse'.
    """
    # Logging-Stream für alle print-Ausgaben
    ERGEBNISSE_PATH.mkdir(parents=True, exist_ok=True)
    log_stream = io.StringIO()
    orig_stdout = sys.stdout
    DATA_ROH_PATH.mkdir(parents=True, exist_ok=True)
    DATA_BEARBEITET_PATH.mkdir(parents=True, exist_ok=True)
    # Verwende ausschließlich context.filename_ohne_ext für alle Dateinamen
    print(f"[LOG] Verwende filename_ohne_ext aus context: {context.filename_ohne_ext}")
    input_name = f"feature_{context.filename_ohne_ext}_umgerechnet.csv"
    input_file = DATA_ROH_PATH / input_name
    output_name = f"feature_{context.filename_ohne_ext}_umgerechnet_ema.csv"
    output_file = DATA_BEARBEITET_PATH / output_name
    ergebnis_ordner = ERGEBNISSE_PATH / context.filename_ohne_ext
    ergebnis_ordner.mkdir(parents=True, exist_ok=True)
    log_datei = ergebnis_ordner / f"analyse_log_{context.filename_ohne_ext}.txt"
    with open(log_datei, "w", encoding="utf-8") as logf:
        successful = 0
        failed = 0
        try:
            sys.stdout = log_stream
            print(f"[DEBUG] filename_ohne_ext aus context: {context.filename_ohne_ext}")
            print(f"[DEBUG] Erwartete Eingabedatei: {input_file}")
            print(f"[DEBUG] Existiert Eingabedatei? {input_file.exists()}")
            print(f"[DEBUG] Ziel-Ausgabedatei: {output_file}")
            print("ERWEITERTE SENSORWERTE-ANALYSE")
            print("=" * 70)
            print("Features: EMA, Z-Score, Gas-Events, ML-Anomalien")
            print("=" * 70)
            if input_file.exists():
                ok = process_csv_file(input_file, output_file)
                print(f"[LOG] Existiert Ausgabedatei nach Verarbeitung? {output_file.exists()}")
                if ok and output_file.exists():
                    successful += 1
                    print(f"Erfolgreich verarbeitet: {output_file}")
                else:
                    failed += 1
                    print(f"Fehler bei Verarbeitung: {input_file}")
            else:
                print(f"[ERROR] Eingabedatei nicht gefunden: {input_file}")
                failed += 1
            print("=" * 70)
            print(f"ANALYSE ABGESCHLOSSEN:")
            print(f"Erfolgreich: {successful}")
            print(f"Fehlgeschlagen: {failed}")
            print(f"Ausgabe in: {DATA_BEARBEITET_PATH}")
        finally:
            sys.stdout = orig_stdout
            logf.write(log_stream.getvalue())
    print(f"Analyse-Log geschrieben nach: {log_datei}")
    info_txt_path = get_info_txt_path(korrekter_filename_ohne_ext)
    info_dir = os.path.dirname(info_txt_path)
    os.makedirs(info_dir, exist_ok=True)
    with open(info_txt_path, 'a', encoding='utf-8') as f:
        f.write("\n\n--- Erweiterte Sensoranalyse ---\n")
        f.write(log_stream.getvalue())
    print(f"Analyse-Log an {info_txt_path} angehängt.")


def process_single_csv_file():
    """
    Verarbeitet gezielt die Datei feature_{context.filename_ohne_ext}_umgerechnet.csv aus bearbeitet2 und schreibt Ergebnis/Log in bearbeitet3 und ergebnisse.
    Erstellt ein ausführliches Log mit allen Schritten und Fehlern.
    """
    from pathlib import Path
    import io
    import sys
    ERGEBNISSE_PATH = Path(__file__).parent.parent.parent / "data" / "ergebnisse"
    DATA_ROH_PATH = Path(__file__).parent.parent.parent / "data" / "bearbeitet2"
    DATA_BEARBEITET_PATH = Path(__file__).parent.parent.parent / "data" / "bearbeitet3"
    ERGEBNISSE_PATH.mkdir(parents=True, exist_ok=True)
    DATA_ROH_PATH.mkdir(parents=True, exist_ok=True)
    DATA_BEARBEITET_PATH.mkdir(parents=True, exist_ok=True)
    log_stream = io.StringIO()
    orig_stdout = sys.stdout
    # Dateiname und Pfade
    input_name = f"feature_{context.filename_ohne_ext}_umgerechnet.csv"
    input_file = DATA_ROH_PATH / input_name
    output_name = f"feature_{context.filename_ohne_ext}_umgerechnet_ema.csv"
    output_file = DATA_BEARBEITET_PATH / output_name
    ergebnis_ordner = ERGEBNISSE_PATH / context.filename_ohne_ext
    ergebnis_ordner.mkdir(parents=True, exist_ok=True)
    log_datei = ergebnis_ordner / f"analyse_log_{context.filename_ohne_ext}.txt"
    info_txt_path = get_info_txt_path(context.filename_ohne_ext)
    info_dir = os.path.dirname(info_txt_path)
    os.makedirs(info_dir, exist_ok=True)
    # Logging
    with open(log_datei, "w", encoding="utf-8") as logf:
        sys.stdout = log_stream
        print(f"[LOG] Starte Verarbeitung: {input_file}")
        print(f"[LOG] Erwartete Ausgabedatei: {output_file}")
        print(f"[LOG] filename_ohne_ext aus context: {context.filename_ohne_ext}")
        print(f"[LOG] Existiert Eingabedatei? {input_file.exists()}")
        if not input_file.exists():
            print(f"[ERROR] Eingabedatei nicht gefunden: {input_file}")
            sys.stdout = orig_stdout
            logf.write(log_stream.getvalue())
            return
        ok = process_csv_file(input_file, output_file)
        print(f"[LOG] Verarbeitung abgeschlossen. Rückgabewert: {ok}")
        print(f"[LOG] Existiert Ausgabedatei nach Verarbeitung? {output_file.exists()}")
        if ok and output_file.exists():
            print(f"[SUCCESS] Datei verarbeitet und gespeichert: {output_file}")
        else:
            print(f"[FAIL] Verarbeitung fehlgeschlagen oder Datei nicht geschrieben: {output_file}")
        sys.stdout = orig_stdout
        logf.write(log_stream.getvalue())
    print(f"Analyse-Log geschrieben nach: {log_datei}")
    with open(info_txt_path, 'a', encoding='utf-8') as f:
        f.write("\n\n--- Erweiterte Sensoranalyse ---\n")
        with open(log_datei, "r", encoding="utf-8") as lf:
            f.write(lf.read())
    print(f"Analyse-Log an {info_txt_path} angehängt.")


if __name__ == "__main__":
    main()