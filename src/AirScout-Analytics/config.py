"""
config.py
Konfigurationseinstellungen für das Projekt.
Hier werden globale Einstellungen und Parameter definiert.
"""
import datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Dict, List, Tuple, Union, Optional, Any


def aktuelle_version() -> str:
    """Gibt einen Zeitstempel für die aktuelle Version zurück."""
    return datetime.datetime.now().strftime("%Y-%m-%d--%H:%M:%SMESZ")


# Projektpfade berechnen
PROJECT_ROOT: Path = Path(__file__).parent.parent.parent
DATA_ROOT: Path = PROJECT_ROOT / "data"

CONFIG = SimpleNamespace(
    # Projekt-Grundkonfiguration
    BASIS_PFAD=str(PROJECT_ROOT),
    PROJEKT_PFAD=str(PROJECT_ROOT),
    PROJEKT_NAME="006_Umweltkontrollsystem",
    PROJEKT_BESCHREIBUNG="Umweltkontrollsystem für Gassensor-Datenanalyse",
    PROJEKT_TYP="Python-Projekt",
    PROJEKT_KATEGORIE="Softwareentwicklung",
    PROJEKT_SCHLAGWORTE=["Python", "Gassensoren", "Datenanalyse", "IoT"],
    PROJEKT_ZIELGRUPPE="Entwickler für Umweltmessungen",
    DATEN_PFAD = "daten/umweltlog.csv"
    BILD_GENERATOR_BEFEHL = "python3 local_generate_image.py --prompt '{prompt}' --output '{output_path}'"
"


    EMAIL=f"script-{aktuelle_version()}@watchkido.de",
    AUTOR="Frank Albrecht",
    VERSION=aktuelle_version(),
    LIZENZ="MIT License",
    GITHUB_USER="watchkido",
    
    # Ordnerstruktur (relative Pfade)
    ORDNER_STRUKTUR=[
        "src/006_Umweltkontrollsystem",
        "src/006_Umweltkontrollsystem/utils",
        "tests",
        "docs",
        "prompts",
        "datenbank",
        "scripts",
        "data/roh",
        "data/bearbeitet",
        "data/ergebnisse",
        "data/fertig",
        "data/praesentation",
        "data/zusammengeführt",
        "data/zwischenspeicher",
        "notebooks",
    ],
    
    # Allgemeine Einstellungen
    REQUIREMENTS="requirements.txt",
    DEBUG=False,
    LOG_LEVEL="INFO",
    DEFAULT_ENCODING="utf-8",
    SPRACHE="de",
    
    # Sensor-Kalibrierung basierend auf realistischen Messwerten
    # Waldstation Pfälzerwald-Hortenkopf: NO2=1-3 µg/m³, CnHm=9-17 µg/m³
    SENSOR_KALIBRIERUNG={
        # R0-Werte für saubere Luft (höhere Werte = niedrigere ppm)
        'R0_VALUES': {
            'MQ2': 2000,   # LPG/Propan - entspricht CnHm ~10-20 µg/m³
            'MQ3': 1800,   # Alkohol
            'MQ4': 2200,   # Methan
            'MQ5': 2000,   # LPG
            'MQ6': 1900,   # LPG/Butan
            'MQ7': 2500,   # CO - sehr niedrige Werte erwartet
            'MQ8': 1700,   # Wasserstoff
            'MQ9': 2100,   # CO/brennbare Gase
            'MQ135': 3000  # NO2 - entspricht 1-5 µg/m³ (realistisch)
        },
        
        # Anpassungsfaktoren für realistische ppm-Werte
        'KALIBRIERUNG_FAKTOREN': {
            'MQ2': 0.01,    # Reduziert für realistische CnHm-Werte
            'MQ3': 0.02,    # Alkohol normalerweise sehr niedrig
            'MQ4': 0.015,   # Methan in Umgebungsluft niedrig
            'MQ5': 0.01,    # LPG sehr niedrig
            'MQ6': 0.01,    # LPG/Butan sehr niedrig
            'MQ7': 0.005,   # CO extrem niedrig (< 1 mg/m³)
            'MQ8': 0.02,    # Wasserstoff normalerweise sehr niedrig
            'MQ9': 0.008,   # CO/brennbare Gase niedrig
            'MQ135': 0.003  # NO2: 1-5 µg/m³ entspricht 0.5-3 ppm
        },
        
        # Zielwerte basierend auf Waldstation (µg/m³)
        'ZIELWERTE_UGM3': {
            'NO2': (1, 5),      # MQ135: 1-5 µg/m³
            'CO': (0.1, 2),     # MQ7/MQ9: sehr niedrig
            'CnHm': (9, 20),    # MQ2/MQ4/MQ5/MQ6: 9-20 µg/m³
            'Alkohol': (0, 5),  # MQ3: praktisch null
            'H2': (0, 10)       # MQ8: sehr niedrig
        },
        
        # Sensor-Modelle für erweiterte Kalibrierung (optional)
        'SENSOR_MODELS': {
            'MQ2': {'A': 100.0, 'B': -1.5},    # LPG, Propan, Wasserstoff
            'MQ3': {'A': 50.0, 'B': -1.3},     # Alkohol (meist niedrig)
            'MQ4': {'A': 80.0, 'B': -1.4},     # Methan
            'MQ5': {'A': 90.0, 'B': -1.6},     # LPG
            'MQ6': {'A': 85.0, 'B': -1.5},     # LPG, Butan
            'MQ7': {'A': 60.0, 'B': -1.2},     # CO (sehr niedrige Werte)
            'MQ8': {'A': 70.0, 'B': -1.4},     # Wasserstoff
            'MQ9': {'A': 75.0, 'B': -1.3},     # CO/Brennbare Gase
            'MQ135': {'A': 40.0, 'B': -1.1}    # NO₂, NH₃ (niedrig)
        },
        
        # Eichstation Referenzwerte (Pfälzerwald-Hortenkopf 15.07.2025)
        'REFERENZ_STATION': {
            'Name': 'Pfälzerwald-Hortenkopf',
            'Datum': '2025-07-15',
            'Uhrzeit': '08:00',
            'Messwerte_ugm3': {
                'PM10': (8, 12),      # Feinstaub
                'PM2.5': (5, 6),      # Ultrafeinstaub
                'O3': (58, 86),       # Ozon (stark schwankend)
                'NO2': (1, 3),        # Stickstoffdioxid
                'NO': (1, 1),         # Stickstoffmonoxid
                'SO2': (1, 1),        # Schwefeldioxid
                'CnHm': (9, 17)       # Kohlenwasserstoffe
            }
        }
    },
    
    # EMA-Analyse und Anomalieerkennung Konfiguration
    EMA_ANALYSE={
        'EMA_SPAN': 5,                      # Span für EMA
        'ZSCORE_THRESHOLD': 2.5,            # Z-Score Schwellenwert
        'GAS_THRESHOLD_MULTIPLIER': 1.5,    # Gas-Ereignis-Schwellen
        'ANOMALY_CONTAMINATION': 0.1,       # Anomalien-Anteil (10%)
        'GAS_EVENT_WINDOW': 20,             # Moving Average Fenster
        'ML_RANDOM_STATE': 42,              # Reproduzierbare ML-Ergebnisse
        'ML_N_ESTIMATORS': 100,             # Anzahl Estimators
        'OUTPUT_SUFFIX': '_ema'             # Suffix für Ausgabedateien
    },
    
    # Dateiverarbeitung Konfiguration
    FILE_PROCESSING={
        'INPUT_ENCODING': 'utf-8',          # Encoding für CSV-Dateien
        'CSV_COMMENT_CHAR': '#',            # Kommentarzeichen für CSV
        # Unterstützte Dateierweiterungen
        'SUPPORTED_EXTENSIONS': ['.csv', '.CSV'],
        'CHUNK_SIZE': None,                 # Chunk-Größe (None = alles)
        'BACKUP_ORIGINAL': False            # Backup der Originaldateien
    },
    
    # Sensor-Identifikation Patterns
    SENSOR_PATTERNS={
        'MQ_SENSORS': r'^MQ\d+$',           # Regex für MQ-Sensoren
        # Keywords für Umweltsensoren
        'ENVIRONMENTAL_KEYWORDS': [
            'temperature', 'humidity', 'light', 'pressure', 'altitude'
        ],
        # Keywords für Header-Erkennung
        'HEADER_KEYWORDS': [
            'MQ', 'Temperature', 'DateTime', 'GPS'
        ]
    },
    
    # Umrechnungskonstanten für Gassensoren
    UMRECHNUNG_KONSTANTEN={
        'MOLAR_VOLUME_STP': 24.45,          # Molares Volumen bei STP (L/mol)
        'PPM_TO_UGM3_FACTOR': 1000,         # Umrechnungsfaktor ppm → µg/m³
        'MAX_REALISTIC_PPM': 1000,          # Maximaler realistischer ppm-Wert
        'MAX_REALISTIC_UGM3': 10000,        # Maximaler realistischer µg/m³
        'MIN_VALID_RATIO': 0,               # Minimum Rs/R0 Verhältnis
        'MAX_VALID_RATIO': 10,              # Maximum Rs/R0 Verhältnis
        'DECIMAL_PLACES': 2,                # Dezimalstellen für Rundung
        'OUTPUT_SUFFIX': '_umgerechnet'     # Suffix für Ausgabedateien
    },
    
    # Molare Massen (g/mol) für Gase mit ppm → µg/m³ Umrechnung
    MOLAR_MASSES={
        'MQ135': 46.0,  # NO₂
        'MQ7': 28.0,    # CO
        'MQ2': 44.0,    # LPG (Propan C3H8)
        'MQ3': 46.0,    # Ethanol C2H5OH
        'MQ4': 16.0,    # Methan CH4
        'MQ5': 44.0,    # LPG (Propan)
        'MQ6': 44.0,    # LPG (Propan)
        'MQ8': 2.0,     # Wasserstoff H2
        'MQ9': 28.0     # CO/Brennbare Gase
    },
    
    # AQI-Umrechnungstabellen (Air Quality Index)
    # US EPA AQI Breakpoints für verschiedene Schadstoffe
    AQI_BREAKPOINTS={
        'PM2.5': [  # µg/m³
            (0.0, 12.0, 0, 50),      # Good
            (12.1, 35.4, 51, 100),   # Moderate
            (35.5, 55.4, 101, 150),  # Unhealthy for Sensitive Groups
            (55.5, 150.4, 151, 200),  # Unhealthy
            (150.5, 250.4, 201, 300),  # Very Unhealthy
            (250.5, 500.4, 301, 500)  # Hazardous
        ],
        'PM10': [  # µg/m³
            (0, 54, 0, 50),
            (55, 154, 51, 100),
            (155, 254, 101, 150),
            (255, 354, 151, 200),
            (355, 424, 201, 300),
            (425, 604, 301, 500)
        ],
        'NO2': [  # µg/m³ (converted from ppb)
            (0, 67, 0, 50),        # 0-35 ppb
            (68, 134, 51, 100),    # 36-70 ppb
            (135, 200, 101, 150),  # 71-105 ppb
            (201, 267, 151, 200),  # 106-140 ppb
            (268, 400, 201, 300),  # 141-210 ppb
            (401, 603, 301, 500)   # 211-315 ppb
        ],
        'CO': [  # µg/m³ (converted from ppm)
            (0, 4636, 0, 50),      # 0-4.0 ppm
            (4637, 9271, 51, 100),  # 4.1-8.0 ppm
            (9272, 12008, 101, 150),  # 8.1-10.4 ppm
            (12009, 15444, 151, 200),  # 10.5-13.4 ppm
            (15445, 18080, 201, 300),  # 13.5-15.7 ppm
            (18081, 22716, 301, 500)  # 15.8-19.7 ppm
        ],
        'O3': [  # µg/m³ (8-hour average, converted from ppm)
            (0, 108, 0, 50),       # 0-0.054 ppm
            (109, 140, 51, 100),   # 0.055-0.070 ppm
            (141, 168, 101, 150),  # 0.071-0.084 ppm
            (169, 208, 151, 200),  # 0.085-0.104 ppm
            (209, 748, 201, 300),  # 0.105-0.374 ppm
            (749, 999, 301, 500)   # 0.375-0.504 ppm
        ]
    },
    
    # AQI-Kategorien mit Beschreibungen
    AQI_CATEGORIES={
        (0, 50): ('Good', 'Grün', 'Luftqualität ist zufriedenstellend'),
        (51, 100): ('Moderate', 'Gelb', 'Luftqualität ist akzeptabel'),
        (101, 150): ('Unhealthy for Sensitive Groups', 'Orange',
                      'Empfindliche Personen können Probleme haben'),
        (151, 200): ('Unhealthy', 'Rot', 'Jeder kann Probleme haben'),
        (201, 300): ('Very Unhealthy', 'Lila', 'Gesundheitswarnung'),
        (301, 500): ('Hazardous', 'Kastanienbraun', 'Notfall-Bedingungen')
    },
    
    # Sensor-zu-Schadstoff-Mapping für AQI-Berechnung
    SENSOR_TO_POLLUTANT_MAPPING={
        'MQ135': 'NO2',   # NO₂
        'MQ7': 'CO',      # CO
        'MQ9': 'CO',      # CO/brennbare Gase
        # PM-Sensoren (falls vorhanden)
        'PM2.5': 'PM2.5',
        'PM10': 'PM10',
        'O3': 'O3'
    },
    
    # AQI-Sensoren die AQI-Unterstützung haben
    AQI_SUPPORTED_SENSORS=['MQ7', 'MQ9', 'MQ135'],
    
    # CSV-Analyzer Konfiguration
    CSV_ANALYZER={
        'HIGH_CORRELATION_THRESHOLD': 0.7,      # Schwellenwert Korrelationen
        'DEFAULT_CSV_FOLDER': str(DATA_ROOT / "roh"),  # Standard CSV-Ordner
        'ENVIRONMENTAL_KEYWORDS': ['temp', 'humid', 'light', 'gps'],
        'TIME_KEYWORDS': ['time', 'date', 'sec'],  # Keywords für Zeitspalten
        'MQ_SENSOR_IDENTIFIER': 'MQ',           # Identifikator für MQ-Sensoren
        'REPORT_ENCODING': 'utf-8',             # Encoding für Report-Dateien
        'DECIMAL_PLACES': 2,                    # Dezimalstellen für Statistiken
        'FILE_SIZE_UNIT': 1024,                 # Divisor für Dateigröße in KB
        'OUTPUT_SUFFIXES': {                    # Suffixe für Output-Dateien
            'INFO_TXT': '_info.txt',
            'INFO_CSV': '_info.csv'
        }
    },
    
    # Projekt-Analyse Konfiguration
    PROJEKT_ANALYSE={
        'OUTPUT_DIR': str(DATA_ROOT / "fertig"),     # Ausgabeordner
        'OUTPUT_FILENAME': 'import_analyse_ergebnis.txt',  # Ausgabedatei
        'EXCLUDED_DIRS': ['.venv', '.git', '__pycache__'],  # Ausgeschlossen
        'TREE_CONNECTOR_LAST': '└── ',              # Letzter Baum-Connector
        'TREE_CONNECTOR_MIDDLE': '├── ',            # Mittlerer Baum-Connector
        'TREE_PREFIX_LAST': '    ',                 # Prefix letzter Eintrag
        'TREE_PREFIX_MIDDLE': '│   ',               # Prefix mittlerer Eintrag
        'MODULE_NAME_WIDTH': 20,                    # Breite für Modulnamen
        'TREE_SEPARATOR_LENGTH': 60,                # Länge der Trennlinie
        'FILE_ENCODING': 'utf-8',                   # Encoding Ausgabedateien
        'PYTHON_EXTENSION': '.py',                  # Python-Dateierweiterung
        'FLAKE8_REQUIRED': True,                    # Flake8-Prüfung erforderlich
        'DOTFILE_PREFIX': '.'                       # Prefix versteckte Dateien
    }
)