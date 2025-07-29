
import pandas as pd
import numpy as np
from pathlib import Path

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

import sys
import io
from config import CONFIG
from context import filename_ohne_ext


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
from context import filename_ohne_ext


# Projektpfade definieren
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_ROH_PATH = PROJECT_ROOT / "data" / "bearbeitet2"
DATA_BEARBEITET_PATH = PROJECT_ROOT / "data" / "bearbeitet3"
ERGENISSE_PATH = PROJECT_ROOT / "data" / "ergebnisse"


def apply_ema_smoothing(df, sensor_groups):
    """
    Wendet Exponential Moving Average auf alle Sensorspalten an
    (bestimmte Spalten wie GPS, Radiation_CPS, *_zscore, *_outlier etc. werden explizit ausgeschlossen)
    """
    df_ema = df.copy()
    print(f"  → EMA-Glättung für {len(sensor_groups['all_sensors'])} Sensoren")
    # Spalten, die niemals geglättet werden sollen
    ausnahme_spalten = [
        "GPS_Lat", "GPS_Lon", "GPS_Alt", "GPS_Speed", "GPS_Course", "GPS_Sats",
        "Radiation_CPS"
    ]
    ausnahme_spalten += [col for col in df.columns if any(
        col.endswith(suffix) for suffix in ["_zscore", "_outlier", "_event", "_intensity", "_anomaly", "_score"]
    )]
    for sensor in sensor_groups['all_sensors']:
        if sensor in df.columns and sensor not in ausnahme_spalten:
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
    try:
        print(f"Verarbeite: {input_file.name}")
        # 1. CSV laden und Header bereinigen
        df = clean_csv_header(input_file)
        print(f"Spalten im DataFrame: {df.columns.tolist()}")  # Debug-Ausgabe
        if df.empty:
            print("  → Datei ist leer!")
            return False
        # 2. Sensorspalten identifizieren
        sensor_groups = identify_sensor_columns(df)
        print(f"Erkannte Sensorspalten: {sensor_groups.get('all_sensors', [])}")  # Debug-Ausgabe
        if not sensor_groups['all_sensors']:
            print("  → Keine Sensorspalten gefunden!")
            return False
        print(f"  → {len(sensor_groups['mq_sensors'])} MQ-Sensoren, "
              f"{len(sensor_groups['environmental'])} Umweltsensoren")
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
            print(f"  → Gespeichert in bearbeitet3: {output_file}")
            if not output_file.exists():
                print(f"  → Fehler: Datei wurde nicht gespeichert! Pfad: {output_file}")
        except Exception as e:
            print(f"  → Fehler beim Speichern in bearbeitet3: {e}")
        # 9. Zusammenfassung
        print_analysis_summary(df_processed, sensor_groups)
        return True
    except Exception as e:
        print(f"  → Fehler bei {input_file.name}: {str(e)}")
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
    ERGENISSE_PATH.mkdir(parents=True, exist_ok=True)
    log_stream = io.StringIO()
    orig_stdout = sys.stdout
    # Statusmeldungen direkt ins Terminal
    print("Datei name:", filename_ohne_ext)
    DATA_ROH_PATH.mkdir(parents=True, exist_ok=True)
    DATA_BEARBEITET_PATH.mkdir(parents=True, exist_ok=True)
    csv_files = list({f.resolve() for f in DATA_ROH_PATH.glob("*.csv")})
    print(f"Gefundene CSV-Dateien in {DATA_ROH_PATH}: {len(csv_files)}")
    if csv_files:
        print("Dateinamen:", [f.name for f in csv_files])
    else:
        print(f"Keine CSV-Dateien in {DATA_ROH_PATH} gefunden!")
        return
    print("ERWEITERTE SENSORWERTE-ANALYSE")
    print("=" * 70)
    print("Features: EMA, Z-Score, Gas-Events, ML-Anomalien")
    print("=" * 70)
    successful = 0
    failed = 0
    sys.stdout = log_stream
    for csv_file in csv_files:
        # Erstelle Ausgabe-Dateinamen
        output_name = f"{csv_file.stem}{OUTPUT_SUFFIX}.csv"
        output_file = DATA_BEARBEITET_PATH / output_name
        # Verarbeite die Datei
        if process_csv_file(csv_file, output_file):
            successful += 1
        else:
            failed += 1
        print()  # Leerzeile zwischen Dateien
    print("=" * 70)
    print(f"ANALYSE ABGESCHLOSSEN:")
    print(f"Erfolgreich: {successful}")
    print(f"Fehlgeschlagen: {failed}")
    print(f"Ausgabe in: {DATA_BEARBEITET_PATH}")
    sys.stdout = orig_stdout
    info_txt_path = get_info_txt_path(filename_ohne_ext)
    # Ordner sicherstellen
    info_dir = os.path.dirname(info_txt_path)
    os.makedirs(info_dir, exist_ok=True)
    with open(info_txt_path, 'a', encoding='utf-8') as f:
        f.write("\n\n--- Erweiterte Sensoranalyse ---\n")
        f.write(log_stream.getvalue())
    print(f"Analyse-Log an {info_txt_path} angehängt.")


if __name__ == "__main__":
    main()