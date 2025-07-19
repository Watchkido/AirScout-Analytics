"""
konstanten.py
Spezielle Konstanten für Datenanalyse und Utilities.
Hier werden häufig genutzte Konstanten zentral abgelegt.
"""

from types import SimpleNamespace
import numpy as np

CONFIG = SimpleNamespace(
    SEED=42,                        # Zufalls-Seed für Reproduzierbarkeit
    TRAIN_TEST_SPLIT=0.8,           # Anteil Trainingsdaten
    VALIDATION_SPLIT=0.1,           # Anteil Validierungsdaten
    MISSING_VALUE=np.nan,           # Platzhalter für fehlende Werte
    EPSILON=1e-8,                   # Kleine Zahl für numerische Stabilität
    DATETIME_FORMAT="%Y-%m-%d",     # Standard-Datumsformat
    TARGET_COLUMN="label",          # Name der Zielspalte
    FEATURE_COLUMNS=[],             # Liste der Feature-Spaltennamen
    RANDOM_STATE=42,                # Für Scikit-Learn-Modelle
    N_JOBS=-1,                      # Anzahl paralleler Prozesse
    FIGURE_SIZE=(10, 6),            # Standardgröße für Plots
    COLOR_PALETTE="tab10",          # Standard-Farbpalette
    ALPHA=0.7,                      # Transparenzwert für Plots
    MAX_ITER=1000,                  # Maximale Iterationen für Algorithmen
    TOL=1e-4,                       # Toleranz für Konvergenz
    ENCODING="utf-8",               # Standard-Encoding für Dateien
    CSV_DELIMITER=","               # Trennzeichen für CSV-Dateien
)

HELLO = 'Hallo aus utils!'

if __name__ == "__main__":
    print("Beispiel-Konfiguration für Datenanalyse:")
    for k, v in CONFIG.__dict__.items():
        print(f"{k}: {v}")