"""
projekt_analyse_optimiert.py
============================

Optimiertes Modul zur Analyse von Python-Projekten hinsichtlich ihrer
Datei- und Importstruktur sowie zur Durchführung einer Flake8-Codeprüfung.

Features:
- Rekursive Suche nach Python-Dateien mit konfigurierbaren Ausschlüssen
- Analyse von Import-Abhängigkeiten zwischen Modulen
- Baumstruktur-Darstellung des Projektverzeichnisses
- Flake8-Codequalitätsprüfung
- Externe Library-Analyse mit detailliertem Import-Tracking
- Alle magischen Zahlen und Pfade zentralisiert in config.py
- Vollständige Type Hints für bessere IDE-Unterstützung
- Ausgabe nach data/fertig Verzeichnis

Abhängigkeiten:
---------------
- os, re, subprocess
- collections.defaultdict
- pathlib.Path
- typing (Dict, List, Set, Tuple, Optional, Any)
- datetime
- config.CONFIG (externe Konfigurationsdatei)
- flake8 (optional, muss installiert sein)

Autor: Frank Albrecht
Datum: 15.07.2025
"""
import os
import re
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from config import CONFIG


def sammle_python_dateien() -> List[str]:
    """
    Sammelt alle Python-Dateien im Projekt.
    
    :returns: Liste aller Python-Dateipfade
    :rtype: List[str]
    :example:

        >>> dateien = sammle_python_dateien()
        >>> print(len(dateien))
        15

    """
    py_dateien: List[str] = []
    
    for root, dirs, files in os.walk(CONFIG.PROJEKT_PFAD):
        # Überspringe bestimmte Verzeichnisse
        dirs[:] = [d for d in dirs
                   if d not in CONFIG.PROJEKT_ANALYSE['EXCLUDED_DIRS']]
        
        for file in files:
            if file.endswith(CONFIG.PROJEKT_ANALYSE['PYTHON_EXTENSION']):
                py_dateien.append(os.path.join(root, file))
    
    return py_dateien


def extrahiere_alle_imports(dateipfad: str) -> Tuple[Set[str], 
                                                  Dict[str, List[str]]]:
    """
    Extrahiert alle importierten Module aus einer Python-Datei.
    Unterscheidet zwischen einfachen Imports und detaillierten from-Imports.
    
    :param dateipfad: Pfad zur Python-Datei
    :type dateipfad: str
    :returns: Tuple aus (alle_imports, from_imports_details)
    :rtype: Tuple[Set[str], Dict[str, List[str]]]
    :example:

        >>> alle, details = extrahiere_alle_imports("main.py")
        >>> print(alle)
        {'os', 'sys', 'pandas'}
        >>> print(details)
        {'pandas': ['DataFrame', 'read_csv'], 'os': ['path']}

    """
    imports: Set[str] = set()
    from_imports_details: Dict[str, List[str]] = defaultdict(list)
    encoding: str = CONFIG.PROJEKT_ANALYSE['FILE_ENCODING']
    
    try:
        with open(dateipfad, "r", encoding=encoding, errors="ignore") as f:
            for zeile in f:
                # Einfache imports: import pandas, import os
                match_import = re.match(r'^\s*import\s+([\w\.]+)', zeile)
                # From imports: from pandas import DataFrame
                match_from = re.match(r'^\s*from\s+([\w\.]+)\s+import\s+(.+)', zeile)
                
                if match_import:
                    module_name = match_import.group(1).split('.')[0]
                    imports.add(module_name)
                elif match_from:
                    module_name = match_from.group(1).split('.')[0]
                    imported_items = match_from.group(2)
                    imports.add(module_name)
                    
                    # Parse die importierten Items (kann mehrere durch Kommas getrennt sein)
                    items = [item.strip() for item in imported_items.split(',')]
                    for item in items:
                        # Entferne "as alias" wenn vorhanden
                        clean_item = item.split(' as ')[0].strip()
                        if clean_item and clean_item != '*':
                            from_imports_details[module_name].append(clean_item)
                            
    except FileNotFoundError:
        print(f"⚠️ Datei nicht gefunden: {dateipfad}")
    
    return imports, dict(from_imports_details)


def erstelle_modul_mapping(py_dateien: List[str]) -> Dict[str, str]:
    """
    Erstellt ein Mapping von Modulnamen zu Dateipfaden für interne Module.
    
    :param py_dateien: Liste aller Python-Dateien
    :type py_dateien: List[str]
    :returns: Mapping von Modulnamen zu Dateipfaden
    :rtype: Dict[str, str]
    :example:

        >>> mapping = erstelle_modul_mapping(['src/main.py', 'src/config.py'])
        >>> print(mapping)
        {'main': 'src/main.py', 'config': 'src/config.py'}

    """
    modul_mapping: Dict[str, str] = {}
    
    for datei in py_dateien:
        modul_name = os.path.splitext(os.path.basename(datei))[0]
        if modul_name != '__init__':  # Überspringe __init__.py Dateien
            modul_mapping[modul_name] = datei
    
    return modul_mapping


def analysiere_externe_libraries(py_dateien: List[str], 
                                projekt_module: Dict[str, str]) -> Dict[str, Dict[str, List[str]]]:
    """
    Analysiert externe Libraries und deren Verwendung in den Projektdateien.
    
    :param py_dateien: Liste aller Python-Dateien
    :type py_dateien: List[str]
    :param projekt_module: Mapping von Modulnamen zu Dateipfaden (interne Module)
    :type projekt_module: Dict[str, str]
    :returns: Mapping von Library-Namen zu verwendenden Dateien und Details
    :rtype: Dict[str, Dict[str, List[str]]]
    :example:

        >>> result = analysiere_externe_libraries(['main.py'], {'config': 'config.py'})
        >>> print(result)
        {'pandas': {'verwendet_in': ['main.py'], 'funktionen': ['DataFrame', 'read_csv']}}

    """
    # Standard-Library Module (häufige, aber nicht vollständig)
    standard_libs: Set[str] = {
        'os', 'sys', 'io', 're', 'json', 'csv', 'xml', 'html', 'urllib', 'http',
        'datetime', 'time', 'calendar', 'collections', 'itertools', 'functools',
        'operator', 'pathlib', 'glob', 'tempfile', 'shutil', 'pickle', 'sqlite3',
        'logging', 'warnings', 'traceback', 'inspect', 'types', 'copy', 'pprint',
        'math', 'random', 'statistics', 'decimal', 'fractions', 'cmath',
        'threading', 'multiprocessing', 'concurrent', 'subprocess', 'queue',
        'socket', 'ssl', 'email', 'base64', 'hashlib', 'hmac', 'secrets',
        'unittest', 'doctest', 'pdb', 'profile', 'timeit', 'trace',
        'argparse', 'configparser', 'getopt', 'readline', 'rlcompleter'
    }
    
    externe_libs: Dict[str, Dict[str, List[str]]] = {}
    
    for datei in py_dateien:
        alle_imports, from_details = extrahiere_alle_imports(datei)
        datei_name = os.path.basename(datei)
        
        for lib in alle_imports:
            # Überspringe interne Module und Standard-Library
            if lib not in projekt_module and lib not in standard_libs:
                if lib not in externe_libs:
                    externe_libs[lib] = {'verwendet_in': [], 'funktionen': []}
                
                if datei_name not in externe_libs[lib]['verwendet_in']:
                    externe_libs[lib]['verwendet_in'].append(datei_name)
                
                # Füge spezifische importierte Funktionen/Klassen hinzu
                if lib in from_details:
                    for func in from_details[lib]:
                        if func not in externe_libs[lib]['funktionen']:
                            externe_libs[lib]['funktionen'].append(func)
    
    # Sortiere Funktionen alphabetisch
    for lib in externe_libs:
        externe_libs[lib]['funktionen'].sort()
    
    return externe_libs


def analysiere_code_statistiken(py_dateien: List[str]) -> Dict[str, Any]:
    """
    Analysiert Code-Statistiken für alle Python-Dateien.
    
    :param py_dateien: Liste aller Python-Dateien
    :type py_dateien: List[str]
    :returns: Dictionary mit Statistiken
    :rtype: Dict[str, Any]
    :example:

        >>> stats = analysiere_code_statistiken(['main.py'])
        >>> print(stats['gesamt_zeilen'])
        500

    """
    statistiken: Dict[str, Any] = {
        'datei_anzahl': len(py_dateien),
        'gesamt_zeilen': 0,
        'code_zeilen': 0,
        'kommentar_zeilen': 0,
        'leer_zeilen': 0,
        'datei_details': {}
    }
    
    for datei in py_dateien:
        try:
            with open(datei, 'r', encoding='utf-8') as f:
                zeilen = f.readlines()
                
            datei_stats = {
                'gesamt': len(zeilen),
                'code': 0,
                'kommentare': 0,
                'leer': 0
            }
            
            for zeile in zeilen:
                zeile_stripped = zeile.strip()
                if not zeile_stripped:
                    datei_stats['leer'] += 1
                elif zeile_stripped.startswith('#'):
                    datei_stats['kommentare'] += 1
                else:
                    datei_stats['code'] += 1
            
            # Aktualisiere Gesamtstatistiken
            statistiken['gesamt_zeilen'] += datei_stats['gesamt']
            statistiken['code_zeilen'] += datei_stats['code']
            statistiken['kommentar_zeilen'] += datei_stats['kommentare']
            statistiken['leer_zeilen'] += datei_stats['leer']
            
            # Speichere Datei-Details
            datei_name = os.path.basename(datei)
            statistiken['datei_details'][datei_name] = datei_stats
            
        except Exception as e:
            print(f"⚠️  Fehler beim Lesen von {datei}: {e}")
    
    return statistiken


def analysiere_abhängigkeiten(py_dateien: List[str]) -> Dict[str, List[str]]:
    """
    Analysiert Import-Abhängigkeiten zwischen Modulen.
    
    :param py_dateien: Liste aller Python-Dateien
    :type py_dateien: List[str]
    :returns: Dictionary mit Abhängigkeiten
    :rtype: Dict[str, List[str]]
    :example:

        >>> deps = analysiere_abhängigkeiten(['main.py'])
        >>> print(deps)
        {'main.py': ['config', 'utils']}

    """
    abhängigkeiten: Dict[str, List[str]] = {}
    
    for datei in py_dateien:
        datei_name = os.path.basename(datei)
        abhängigkeiten[datei_name] = []
        
        alle_imports, _ = extrahiere_alle_imports(datei)
        
        # Filtere nur interne Imports (relative zu unserem Projekt)
        for import_name in alle_imports:
            # Prüfe ob es ein internes Modul ist
            modul_gefunden = any(import_name in os.path.basename(py_datei) 
                               for py_datei in py_dateien)
            if modul_gefunden:
                abhängigkeiten[datei_name].append(import_name)
    
    return abhängigkeiten


def print_statistiken(statistiken: Dict[str, Any]) -> None:
    """
    Gibt Code-Statistiken formatiert auf der Konsole aus.
    
    :param statistiken: Dictionary mit Statistiken
    :type statistiken: Dict[str, Any]
    :returns: Nichts (Ausgabe auf Konsole)
    :rtype: None
    :example:

        >>> stats = {'datei_anzahl': 5, 'gesamt_zeilen': 100}
        >>> print_statistiken(stats)
        📈 Code-Statistiken:
        ...

    """
    print("📈 Code-Statistiken:")
    print(f"   📄 Dateien: {statistiken['datei_anzahl']}")
    print(f"   📏 Zeilen gesamt: {statistiken['gesamt_zeilen']:,}")
    print(f"   💻 Code-Zeilen: {statistiken['code_zeilen']:,}")
    print(f"   💬 Kommentar-Zeilen: {statistiken['kommentar_zeilen']:,}")
    print(f"   📝 Leer-Zeilen: {statistiken['leer_zeilen']:,}")
    
    if statistiken['gesamt_zeilen'] > 0:
        gesamt = statistiken['gesamt_zeilen']
        code_anteil = (statistiken['code_zeilen'] / gesamt) * 100
        kommentar_anteil = (statistiken['kommentar_zeilen'] / gesamt) * 100
        print(f"   📊 Code-Anteil: {code_anteil:.1f}%")
        print(f"   📊 Kommentar-Anteil: {kommentar_anteil:.1f}%")


def print_abhängigkeiten(abhängigkeiten: Dict[str, List[str]]) -> None:
    """
    Gibt Modul-Abhängigkeiten formatiert auf der Konsole aus.
    
    :param abhängigkeiten: Dictionary mit Abhängigkeiten
    :type abhängigkeiten: Dict[str, List[str]]
    :returns: Nichts (Ausgabe auf Konsole)
    :rtype: None
    :example:

        >>> deps = {'main.py': ['config', 'utils']}
        >>> print_abhängigkeiten(deps)
        🔗 Modul-Abhängigkeiten:
        ...

    """
    print("🔗 Modul-Abhängigkeiten:")
    
    for modul, deps in abhängigkeiten.items():
        if deps:
            print(f"   📄 {modul} → {', '.join(deps)}")
        else:
            print(f"   📄 {modul} → (keine internen Abhängigkeiten)")


def print_externe_libraries(externe_libs: Dict[str, Dict[str, List[str]]]) -> None:
    """
    Gibt eine strukturierte Übersicht über externe Libraries aus.
    
    :param externe_libs: Mapping von Library-Namen zu Details
    :type externe_libs: Dict[str, Dict[str, List[str]]]
    :returns: None
    :rtype: None
    """
    separator_length: int = CONFIG.PROJEKT_ANALYSE['TREE_SEPARATOR_LENGTH']
    
    print("\n📚 \033[1mExterne Libraries:\033[0m")
    print("".ljust(separator_length, "─"))
    
    if not externe_libs:
        print("  ✅ Keine externen Libraries gefunden (nur Standard-Library verwendet)")
        print("".ljust(separator_length, "─"))
        return
    
    # Sortiere Libraries nach Anzahl der verwendenden Dateien
    sorted_libs = sorted(externe_libs.items(), 
                        key=lambda x: len(x[1]['verwendet_in']), 
                        reverse=True)
    
    for lib_name, details in sorted_libs:
        verwendet_in = details['verwendet_in']
        funktionen = details['funktionen']
        
        print(f"📦 \033[92m{lib_name}\033[0m")
        print(f"   📊 Verwendet in {len(verwendet_in)} Datei(en):")
        
        for datei in verwendet_in:
            print(f"      └── {datei}")
            
        if funktionen:
            print(f"   🔧 Importierte Funktionen/Klassen ({len(funktionen)}):")
            # Zeige maximal 10 Funktionen, dann "..."
            max_show = 10
            for i, func in enumerate(funktionen[:max_show]):
                if i == len(funktionen[:max_show])-1 and len(funktionen) <= max_show:
                    connector = "└── "
                else:
                    connector = "├── "
                print(f"      {connector}{func}")
            if len(funktionen) > max_show:
                print(f"      └── ... und {len(funktionen) - max_show} weitere")
        else:
            print("   🔧 Vollständige Module importiert (import library)")
            
        print("".ljust(separator_length, "─"))


def schreibe_statistik_bericht(statistiken: Dict[str, Any]) -> None:
    """
    Schreibt Code-Statistiken in eine Datei.
    
    :param statistiken: Dictionary mit Statistiken
    :type statistiken: Dict[str, Any]
    :returns: Nichts (schreibt in Datei)
    :rtype: None
    :example:

        >>> stats = {'datei_anzahl': 5}
        >>> schreibe_statistik_bericht(stats)
        # Erstellt code_statistiken.txt

    """
    output_path = os.path.join(CONFIG.PROJEKT_ANALYSE['OUTPUT_DIR'], 'code_statistiken.txt')
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"Code-Statistiken für {CONFIG.PROJEKT_NAME}\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Analyse-Zeitpunkt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("Übersicht:\n")
        f.write(f"- Dateien: {statistiken['datei_anzahl']}\n")
        f.write(f"- Zeilen gesamt: {statistiken['gesamt_zeilen']:,}\n")
        f.write(f"- Code-Zeilen: {statistiken['code_zeilen']:,}\n")
        f.write(f"- Kommentar-Zeilen: {statistiken['kommentar_zeilen']:,}\n")
        f.write(f"- Leer-Zeilen: {statistiken['leer_zeilen']:,}\n\n")
        
        f.write("Details pro Datei:\n")
        for datei, details in statistiken['datei_details'].items():
            f.write(f"- {datei}: {details['gesamt']} Zeilen "
                   f"({details['code']} Code, {details['kommentare']} Kommentare)\n")


def schreibe_abhängigkeits_bericht(abhängigkeiten: Dict[str, List[str]]) -> None:
    """
    Schreibt Abhängigkeits-Analyse in eine Datei.
    
    :param abhängigkeiten: Dictionary mit Abhängigkeiten
    :type abhängigkeiten: Dict[str, List[str]]
    :returns: Nichts (schreibt in Datei)
    :rtype: None
    :example:

        >>> deps = {'main.py': ['config']}
        >>> schreibe_abhängigkeits_bericht(deps)
        # Erstellt abhängigkeiten.txt

    """
    output_path = os.path.join(CONFIG.PROJEKT_ANALYSE['OUTPUT_DIR'], 'abhängigkeiten.txt')
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"Modul-Abhängigkeiten für {CONFIG.PROJEKT_NAME}\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Analyse-Zeitpunkt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        for modul, deps in abhängigkeiten.items():
            f.write(f"{modul}:\n")
            if deps:
                for dep in deps:
                    f.write(f"  → {dep}\n")
            else:
                f.write("  → (keine internen Abhängigkeiten)\n")
            f.write("\n")


def schreibe_library_analyse(externe_libs: Dict[str, Dict[str, List[str]]], 
                            output_path: str) -> None:
    """
    Schreibt die Library-Analyse in die Ausgabedatei.
    
    :param externe_libs: Mapping von Library-Namen zu Details
    :type externe_libs: Dict[str, Dict[str, List[str]]]
    :param output_path: Pfad zur Ausgabedatei
    :type output_path: str
    :returns: None
    :rtype: None
    """
    with open(output_path, "w", encoding='utf-8') as f:
        f.write(f"Externe Libraries für {CONFIG.PROJEKT_NAME}\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Analyse-Zeitpunkt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        if not externe_libs:
            f.write("✅ Keine externen Libraries gefunden (nur Standard-Library verwendet)\n")
            return
        
        # Sortiere Libraries nach Anzahl der verwendenden Dateien
        sorted_libs = sorted(externe_libs.items(), 
                            key=lambda x: len(x[1]['verwendet_in']), 
                            reverse=True)
        
        for lib_name, details in sorted_libs:
            verwendet_in = details['verwendet_in']
            funktionen = details['funktionen']
            
            f.write(f"\n📦 {lib_name}\n")
            f.write(f"   Verwendet in {len(verwendet_in)} Datei(en):\n")
            
            for datei in verwendet_in:
                f.write(f"   └── {datei}\n")
                
            if funktionen:
                f.write(f"   Importierte Funktionen/Klassen ({len(funktionen)}):\n")
                for func in funktionen:
                    f.write(f"   ├── {func}\n")
            else:
                f.write("   Vollständige Module importiert (import library)\n")


def neue_hauptfunktion() -> None:
    """
    Führt eine umfassende Projektanalyse durch inklusive Code-Statistiken,
    Abhängigkeiten und externen Libraries.
    
    :returns: Nichts (Ausgabe erfolgt in Konsole und Datei)
    :rtype: None
    :example:

        >>> neue_hauptfunktion()
        # Führt komplette Projektanalyse durch

    """
    projekt_name = CONFIG.PROJEKT_NAME
    trenn_laenge = 70  # Standard-Wert
    
    print(f"📊 Starte umfassende Analyse des Projekts: {projekt_name}")
    print(f"📁 Basis-Verzeichnis: {CONFIG.PROJEKT_PFAD}")
    print("=" * trenn_laenge)
    
    # 1. Sammle alle Python-Dateien
    print("🔍 Sammle Python-Dateien...")
    py_dateien = sammle_python_dateien()
    print(f"✅ {len(py_dateien)} Python-Dateien gefunden")
    
    # 2. Analysiere Code-Statistiken
    print("\n📈 Analysiere Code-Statistiken...")
    statistiken = analysiere_code_statistiken(py_dateien)
    print_statistiken(statistiken)
    
    # 3. Analysiere Abhängigkeiten  
    print("\n🔗 Analysiere Modul-Abhängigkeiten...")
    abhängigkeiten = analysiere_abhängigkeiten(py_dateien)
    print_abhängigkeiten(abhängigkeiten)
    
    # 4. Analysiere externe Libraries
    print("\n📚 Analysiere externe Libraries...")
    projekt_module = erstelle_modul_mapping(py_dateien)
    externe_libs = analysiere_externe_libraries(py_dateien, projekt_module)
    print_externe_libraries(externe_libs)
    
    # 5. Schreibe Berichte in Dateien
    print(f"\n💾 Schreibe Analyse-Berichte...")
    schreibe_statistik_bericht(statistiken)
    schreibe_abhängigkeits_bericht(abhängigkeiten)
    lib_pfad = os.path.join(CONFIG.PROJEKT_ANALYSE['OUTPUT_DIR'], 'externe_libraries.txt')
    schreibe_library_analyse(externe_libs, lib_pfad)
    
    fertig_pfad = CONFIG.PROJEKT_ANALYSE['OUTPUT_DIR']
    print(f"\n✅ Analyse abgeschlossen! Berichte gespeichert in: {fertig_pfad}")
    print("=" * trenn_laenge)


if __name__ == "__main__":
    # Führe die neue umfassende Analyse durch
    neue_hauptfunktion()
