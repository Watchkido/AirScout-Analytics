# Externe Library-Analyse Feature

## Implementiert in projekt_analyse_optimiert.py

**Datum:** 2025-07-13  
**Autor:** Frank Albrecht  
**Version:** 1.2

## 🚀 Neue Features

### 1. Externe Library-Erkennung

Die **Funktion analysiere_externe_libraries()** erkennt automatisch externe Python-Libraries:

**Funktionsweise:**

- **Parameter py_dateien** ist eine Liste aller Python-Dateien im Projekt
- **Parameter projekt_module** ist ein Mapping der internen Module (aus erstelle_modul_mapping())
- **Rückgabewert** ist ein Dictionary mit Library-Namen als Schlüssel

**Standard-Library-Filter:**
Die Funktion unterscheidet zwischen Standard-Python-Libraries und externen Paketen:

```python
standard_libs = {'os', 'sys', 'datetime', 'pathlib', 'collections', ...}
```

### 2. Import-Parsing mit Regex

Die **Funktion extrahiere_alle_imports()** verwendet Regex-Patterns für präzises Import-Parsing:

**Regex-Pattern für import-Statements:**

- `r'^\s*import\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)'` für `import module`
- `r'^\s*from\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\s+import'` für `from module import`

**Rückgabewerte:**

- **alle_imports** ist ein Set aller importierten Module
- **from_details** ist ein Dict mit spezifischen importierten Funktionen/Klassen

### 3. Library-Kategorisierung

Das System kategorisiert Libraries automatisch:

**Kategorien:**

- **Standard-Libraries:** Python-interne Module (os, sys, datetime, ...)
- **Externe Libraries:** Third-party Pakete (pandas, numpy, requests, ...)
- **Interne Module:** Projektspezifische Module

**Datenstruktur für externe Libraries:**

```python
{
    'pandas': {
        'verwendet_in': ['data_loader.py', 'analysis.py'],
        'funktionen': ['DataFrame', 'read_csv', 'to_excel']
    },
    'matplotlib': {
        'verwendet_in': ['visualization.py'],
        'funktionen': ['pyplot', 'figure']
    }
}
```

### 4. Ausgabe-Funktionen

#### print_externe_libraries()

**Zweck:** Formatierte Konsolen-Ausgabe der Library-Analyse  
**Ausgabe-Format:**

```
📚 Externe Libraries:
   📦 pandas (verwendet in 2 Dateien)
      → data_loader.py, analysis.py
      → Funktionen: DataFrame, read_csv, to_excel
```

#### schreibe_library_analyse()

**Zweck:** Speichert Library-Analyse in Textdatei  
**Parameter output_path:** Zielpfad für die Ausgabedatei  
**Datei-Format:**

- Header mit Projekt-Name und Zeitstempel
- Übersicht aller externen Libraries
- Details zu Verwendung und importierten Funktionen

### 5. Integration in neue_hauptfunktion()

Die neue Hauptfunktion integriert alle Analyse-Features:

**Ablauf:**

1. **sammle_python_dateien()** - Findet alle .py-Dateien
2. **analysiere_code_statistiken()** - Zählt Zeilen, Code, Kommentare
3. **analysiere_abhängigkeiten()** - Interne Modul-Abhängigkeiten
4. **analysiere_externe_libraries()** - Externe Library-Verwendung
5. **Ausgabe** in Konsole und Dateien

## 📊 Code-Verbesserungen

### Type Hints

Alle Funktionen haben vollständige Type Annotations:

```python
def analysiere_externe_libraries(
    py_dateien: List[str],
    projekt_module: Dict[str, str]
) -> Dict[str, Dict[str, List[str]]]
```

### Magic Numbers eliminiert

Alle konfigurierbaren Werte in config.py zentralisiert:

- `CONFIG.PROJEKT_ANALYSE['projekt_name']`
- `CONFIG.DATA_PATHS.fertig`
- `CONFIG.PROJEKT_ANALYSE['ignorierte_ordner']`

### Relative Pfade

Alle Pfade verwenden pathlib und relative Pfad-Konstruktion:

```python
output_path = os.path.join(CONFIG.DATA_PATHS.fertig, 'externe_libraries.txt')
```

## 🛠️ Verwendung

### Direkte Ausführung

```bash
python projekt_analyse_optimiert.py
```

### Programmatische Verwendung

```python
from projekt_analyse_optimiert import neue_hauptfunktion
neue_hauptfunktion()
```

## 📋 Ausgabedateien

Das System erstellt folgende Dateien in `data/fertig/`:

1. **code_statistiken.txt** - Code-Zeilen-Analyse
2. **abhängigkeiten.txt** - Interne Modul-Abhängigkeiten
3. **externe_libraries.txt** - Externe Library-Verwendung

## 🔧 Konfiguration

Alle Parameter sind in `config.py` konfigurierbar:

```python
PROJEKT_ANALYSE = {
    'projekt_name': 'Umweltkontrollsystem',
    'ignorierte_ordner': ['.git', '__pycache__', '.pytest_cache'],
    'python_datei_endung': '.py',
    'trennzeichen_laenge': 70
}
```

## ✅ Qualitätssicherung

- **PEP 8 konform** - Alle Funktionen folgen Python-Standards
- **Type Safety** - Vollständige Type Hints für IDE-Unterstützung
- **Dokumentation** - Jede Funktion hat ausführliche Docstrings im RST-Format
- **Error Handling** - Try-catch für Datei-Zugriffe
- **Konfigurierbar** - Keine hardcoded Werte im Code

## 🚦 Status: Implementiert ✅

Alle Features sind vollständig implementiert und funktional.
