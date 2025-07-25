# 📋 ANLEITUNG: GASSENSOR-ANALYSE für verschiedene LOG-Dateien

## Verwendung für LOG-Dateien wie "Home-LOG2025-07-12-2258"

### 1. Kommandozeile mit spezifischer Datei:

```
analyse_gassensoren.bat Home-LOG2025-07-12-2258.csv
```

### 2. Interaktive Auswahl (alle CSV-Dateien im Ordner anzeigen):

```
analyse_gassensoren.bat
```

### 3. Python direkt (wenn Umgebung aktiviert):

```python
# Einzelne Datei
e:/dev/projekt_python_venv/006_/.venv/Scripts/python.exe csv_analyzer_gassensor_fixed.py Home-LOG2025-07-12-2258.csv

# Interaktive Auswahl
e:/dev/projekt_python_venv/006_/.venv/Scripts/python.exe csv_analyzer_gassensor_fixed.py
```

## Erstellt automatisch:

### TXT-Report (Lesbar):

- `Home-LOG2025-07-12-2258_info.txt` - Detaillierter Analysereport

### CSV-Export (Maschinenlesbar):

- `Home-LOG2025-07-12-2258_info.csv` - Strukturierte Daten für weitere Analysen

## Unterstützte Dateiformate:

- Kommentierte CSV-Dateien mit `#` am Anfang
- LOG-Dateien mit Gassensor-Daten (MQ-Serie)
- Standard CSV-Dateien mit Sensor-Messungen

## Analysierte Sensoren:

- **MQ-Gassensoren**: MQ2, MQ3, MQ4, MQ5, MQ6, MQ7, MQ8, MQ9, MQ135
- **Umweltsensoren**: Temperatur, Luftfeuchtigkeit, Licht, GPS
- **Zusätzliche**: Mikrofone, Radiation, Zeitstempel

## CSV-Export enthält:

1. **Grunddaten**: Anzahl Datensätze, Spalten, Sensoren
2. **Spalteninformationen**: Datentypen, NULL-Werte, eindeutige Werte
3. **MQ-Statistiken**: mean, std, min, max, 25%, 50%, 75% für jeden Sensor
4. **Korrelationen**: Zwischen allen MQ-Sensor-Paaren
5. **Datenqualität**: Vollständigkeit, fehlende Werte

## Tipps:

- Das Skript erkennt automatisch das CSV-Format
- LOG-Dateien werden bevorzugt angezeigt
- Große Dateien werden mit Dateigröße angezeigt
- Bei Fehlern wird eine detaillierte Fehlermeldung angezeigt
