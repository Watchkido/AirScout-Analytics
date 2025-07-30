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
- Alle magischen Zahlen und Pfade zentralisiert in config.py
- Vollständige Type Hints für bessere IDE-Unterstützung
- Ausgabe nach data/fertig Verzeichnis

Abhängigkeiten:
---------------
- os, re, subprocess
- collections.defaultdict
- pathlib.Path
- typing (Dict, List, Set, Tuple, Optional)
- config.CONFIG (externe Konfigurationsdatei)
- flake8 (optional, muss installiert sein)

Autor: Frank Albrecht
Datum: 15.07.2025
"""
import sys
import os
# Füge src-Verzeichnis zum Python-Pfad hinzu
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src')))
import os
import re
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
from datetime import datetime

from airScout_analytics.config import CONFIG


def finde_python_dateien(root: str) -> List[str]:
    """
    Durchsucht rekursiv den angegebenen Projektordner nach Python-Dateien.
    Ignoriert konfigurierbare Verzeichnisse wie .venv, .git, __pycache__.

    :param root: Startverzeichnis (Projektordner)
    :type root: str
    :returns: Liste aller gefundenen .py-Dateien (mit Pfad)
    :rtype: List[str]
    :example:

        >>> finde_python_dateien("meinprojekt")
        ['meinprojekt/main.py', 'meinprojekt/data/dataset.py']

    """
    py_files: List[str] = []
    excluded_dirs: List[str] = CONFIG.PROJEKT_ANALYSE['EXCLUDED_DIRS']
    python_ext: str = CONFIG.PROJEKT_ANALYSE['PYTHON_EXTENSION']
    
    for ordner, verzeichnisse, dateien in os.walk(root):
        # Ausgeschlossene Verzeichnisse entfernen
        for excluded in excluded_dirs:
            if excluded in verzeichnisse:
                verzeichnisse.remove(excluded)
                
        for datei in dateien:
            if datei.endswith(python_ext):
                pfad: str = os.path.join(ordner, datei)
                py_files.append(os.path.normpath(pfad))
    return py_files


def print_verwendete_module(verwendet_von: Dict[str, List[str]]) -> None:
    """
    Gibt eine strukturierte Übersicht über verwendete Module aus.
    Baut einen Baum zur besseren Visualisierung der Modulabhängigkeiten.
    
    :param verwendet_von: Mapping von Modulnamen zu verwendenden Dateien
    :type verwendet_von: Dict[str, List[str]]
    :returns: None
    :rtype: None
    """
    separator_length: int = CONFIG.PROJEKT_ANALYSE['TREE_SEPARATOR_LENGTH']
    
    print("\n🔗 \033[1mVerwendete Module:\033[0m")
    print("".ljust(separator_length, "─"))
    
    for modul, verwendet_durch in verwendet_von.items():
        print(f"📦 \033[94m{modul}\033[0m")
        # Gruppiere nach Wurzelverzeichnis
        baum: Dict = {}
        for pfad in verwendet_durch:
            teile: List[str] = pfad.split(os.sep)
            d = baum
            for teil in teile:
                d = d.setdefault(teil, {})
                
        def print_baum(d: Dict, prefix: str = "  ") -> None:
            """Rekursive Funktion zur Ausgabe der Baumstruktur."""
            connector_last: str = CONFIG.PROJEKT_ANALYSE['TREE_CONNECTOR_LAST']
            connector_middle: str = CONFIG.PROJEKT_ANALYSE['TREE_CONNECTOR_MIDDLE']
            prefix_last: str = CONFIG.PROJEKT_ANALYSE['TREE_PREFIX_LAST']
            prefix_middle: str = CONFIG.PROJEKT_ANALYSE['TREE_PREFIX_MIDDLE']
            
            for i, (name, sub) in enumerate(d.items()):
                connector = connector_last if i == len(d)-1 else connector_middle
                print(prefix + connector + name)
                if sub:
                    new_prefix = prefix + (prefix_last if i == len(d)-1 else prefix_middle)
                    print_baum(sub, new_prefix)
                    
        print_baum(baum)
        print("".ljust(separator_length, "─"))


def schreibe_kompletten_verzeichnisbaum(dateipfad: str,
                                        wurzelverzeichnis: str) -> None:
    """
    Schreibt vollständige Baumstruktur aller Dateien und Unterordner.
    Ignoriert Ordner die mit konfigurierbarem Prefix beginnen.

    :param dateipfad: Name der Ausgabedatei
    :type dateipfad: str
    :param wurzelverzeichnis: Startverzeichnis für die Baumdarstellung
    :type wurzelverzeichnis: str
    :returns: None
    :rtype: None
    :example:

        >>> schreibe_kompletten_verzeichnisbaum("baum.txt", "meinprojekt")

    """
    def schreibe_baum(pfad: str, prefix: str, f) -> None:
        """Rekursive Funktion zum Schreiben der Baumstruktur."""
        dotfile_prefix: str = CONFIG.PROJEKT_ANALYSE['DOTFILE_PREFIX']
        connector_last: str = CONFIG.PROJEKT_ANALYSE['TREE_CONNECTOR_LAST']
        connector_middle: str = CONFIG.PROJEKT_ANALYSE['TREE_CONNECTOR_MIDDLE']
        prefix_last: str = CONFIG.PROJEKT_ANALYSE['TREE_PREFIX_LAST']
        prefix_middle: str = CONFIG.PROJEKT_ANALYSE['TREE_PREFIX_MIDDLE']
        
        try:
            eintraege: List[str] = sorted(
                [e for e in os.listdir(pfad)
                 if not e.startswith(dotfile_prefix)],
                key=lambda x: (not os.path.isdir(os.path.join(pfad, x)), 
                              x.lower())
            )
        except PermissionError:
            return  # Falls kein Zugriff auf einen Ordner besteht

        for i, eintrag in enumerate(eintraege):
            vollpfad: str = os.path.join(pfad, eintrag)
            ist_letzter: bool = (i == len(eintraege) - 1)
            connector: str = connector_last if ist_letzter else connector_middle
            f.write(f"{prefix}{connector}{eintrag}\n")
            
            if os.path.isdir(vollpfad):
                neues_prefix: str = prefix + (prefix_last if ist_letzter 
                                            else prefix_middle)
                schreibe_baum(vollpfad, neues_prefix, f)

    encoding: str = CONFIG.PROJEKT_ANALYSE['FILE_ENCODING']
    
    with open(dateipfad, "w", encoding=encoding) as f:
        f.write("📄 Alle Dateien und Ordner:\n")
        schreibe_baum(wurzelverzeichnis, "", f)


def schreibe_python_dateien_baum(modulnamen_to_dateien: Dict[str, str], 
                                dateiname: str) -> None:
    """
    Schreibt Baumstruktur aller Python-Dateien in die angegebene Textdatei.

    :param modulnamen_to_dateien: Mapping von Modulnamen zu Dateipfaden
    :type modulnamen_to_dateien: Dict[str, str]
    :param dateiname: Name der Ausgabedatei
    :type dateiname: str
    :returns: None
    :rtype: None
    :example:

        >>> schreibe_python_dateien_baum({'main': 'src/main.py'}, 'baum.txt')

    """
    # Baumstruktur aufbauen
    baum: Dict = {}
    for pfad in modulnamen_to_dateien.values():
        teile: List[str] = os.path.normpath(pfad).split(os.sep)
        d = baum
        for teil in teile[:-1]:
            d = d.setdefault(teil, {})
        d.setdefault('__files__', []).append(teile[-1])

    def schreibe_baum(d: Dict, prefix: str, f) -> None:
        """Rekursive Funktion zum Schreiben der Python-Dateien-Struktur."""
        connector_last: str = CONFIG.PROJEKT_ANALYSE['TREE_CONNECTOR_LAST']
        connector_middle: str = CONFIG.PROJEKT_ANALYSE['TREE_CONNECTOR_MIDDLE']
        prefix_last: str = CONFIG.PROJEKT_ANALYSE['TREE_PREFIX_LAST']
        prefix_middle: str = CONFIG.PROJEKT_ANALYSE['TREE_PREFIX_MIDDLE']
        
        files: List[str] = d.get('__files__', [])
        for i, datei in enumerate(files):
            has_dirs: bool = bool(d.keys() - {'__files__'})
            connector: str = (connector_last if (i == len(files) - 1 and not has_dirs) 
                            else connector_middle)
            f.write(f"{prefix}{connector}{datei}\n")
            
        ordner: List[str] = [k for k in d.keys() if k != '__files__']
        for j, ordname in enumerate(sorted(ordner)):
            ist_letzter: bool = (j == len(ordner) - 1)
            connector: str = connector_last if ist_letzter else connector_middle
            f.write(f"{prefix}{connector}{ordname}\n")
            neues_prefix: str = prefix + (prefix_last if ist_letzter 
                                        else prefix_middle)
            schreibe_baum(d[ordname], neues_prefix, f)

    encoding: str = CONFIG.PROJEKT_ANALYSE['FILE_ENCODING']
    
    with open(dateiname, "w", encoding=encoding) as f:
        f.write("📄 Python-Dateien:\n")
        schreibe_baum(baum, "", f)


def extrahiere_imports(dateipfad: str) -> Set[str]:
    """
    Extrahiert alle importierten Module aus einer Python-Datei.
    
    :param dateipfad: Pfad zur Python-Datei
    :type dateipfad: str
    :returns: Set der importierten Modulnamen
    :rtype: Set[str]
    :raises FileNotFoundError: Wenn die Datei nicht gefunden wird
    :example:

        >>> extrahiere_imports("main.py")
        {'os', 'sys', 'config'}

    """
    imports: Set[str] = set()
    encoding: str = CONFIG.PROJEKT_ANALYSE['FILE_ENCODING']
    
    try:
        with open(dateipfad, "r", encoding=encoding, errors="ignore") as f:
            for zeile in f:
                match_import = re.match(r'^\s*import\s+([\w\.]+)', zeile)
                match_from = re.match(r'^\s*from\s+([\w\.]+)', zeile)
                if match_import:
                    imports.add(match_import.group(1).split('.')[0])
                elif match_from:
                    imports.add(match_from.group(1).split('.')[0])
    except FileNotFoundError:
        print(f"⚠️ Datei nicht gefunden: {dateipfad}")
    
    return imports


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


def analysiere_imports(py_dateien: List[str]) -> Tuple[Dict[str, str], 
                                                     Dict[str, List[str]], 
                                                     List[str]]:
    """
    Analysiert Importbeziehungen zwischen den gefundenen Python-Dateien.
    
    :param py_dateien: Liste aller Python-Dateien
    :type py_dateien: List[str]
    :returns: Tuple aus (modulnamen_to_dateien, verwendet_von, nicht_verwendet)
    :rtype: Tuple[Dict[str, str], Dict[str, List[str]], List[str]]
    :example:

        >>> module, verwendet, ungenutzt = analysiere_imports(['main.py'])
        >>> print(module)
        {'main': 'main.py'}

    """
    python_ext: str = CONFIG.PROJEKT_ANALYSE['PYTHON_EXTENSION']
    
    modulnamen_to_dateien: Dict[str, str] = {
        os.path.splitext(os.path.basename(f))[0]: f for f in py_dateien
    }
    verwendete_module: Set[str] = set()
    verwendet_von: Dict[str, List[str]] = defaultdict(list)

    for datei in py_dateien:
        imports: Set[str] = extrahiere_imports(datei)
        for imp in imports:
            if imp in modulnamen_to_dateien:
                verwendete_module.add(imp)
                verwendet_von[imp].append(datei)
    
    nicht_verwendet: List[str] = [
        f for name, f in modulnamen_to_dateien.items() 
        if name not in verwendete_module
    ]
    
    return modulnamen_to_dateien, verwendet_von, nicht_verwendet


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


def print_externe_libraries(externe_libs: Dict[str, Dict[str, List[str]]]) -> None:
    """
    Gibt eine strukturierte Übersicht über externe Libraries aus.
    
    :param externe_libs: Mapping von Library-Namen zu Details
    :type externe_libs: Dict[str, Dict[str, List[str]]]
    :returns: None
    :rtype: None
    """
    separator_length: int = CONFIG.PROJEKT_ANALYSE['TREE_SEPARATOR_LENGTH']
    module_width: int = CONFIG.PROJEKT_ANALYSE['MODULE_NAME_WIDTH']
    
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
                connector = "└── " if i == len(funktionen[:max_show])-1 and len(funktionen) <= max_show else "├── "
                print(f"      {connector}{func}")
            if len(funktionen) > max_show:
                print(f"      └── ... und {len(funktionen) - max_show} weitere")
        else:
            print("   🔧 Vollständige Module importiert (import library)")
            
        print("".ljust(separator_length, "─"))


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
    encoding: str = CONFIG.PROJEKT_ANALYSE['FILE_ENCODING']
    
    with open(output_path, "a", encoding=encoding) as f:
        f.write("\n📚 EXTERNE LIBRARIES:\n")
        f.write("=" * 50 + "\n")
        
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
                
        f.write("\n" + "=" * 50 + "\n")


def flake8_pruefen(dateien: List[str]) -> None:
    """
    Führt Flake8-Codeanalyse für die übergebenen Python-Dateien durch.
    
    :param dateien: Liste der zu prüfenden Python-Dateien
    :type dateien: List[str]
    :returns: None
    :rtype: None
    :raises FileNotFoundError: Wenn flake8 nicht installiert ist
    """
    print("\n🧪 Flake8 Codeprüfung:")
    
    flake8_required: bool = CONFIG.PROJEKT_ANALYSE['FLAKE8_REQUIRED']
    
    try:
        subprocess.run(["flake8", "--version"], check=True, capture_output=True)
    except FileNotFoundError:
        if flake8_required:
            print("❌ flake8 ist nicht installiert. "
                  "Bitte mit `pip install flake8` installieren.")
        else:
            print("⚠️ flake8 ist nicht installiert. Überspringe Codeprüfung.")
        return

    for datei in dateien:
        print(f"📂 {datei}")
        result = subprocess.run(["flake8", datei], capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        else:
            print("   ✅ Keine Probleme gefunden.")


def erstelle_ausgabeordner() -> str:
    """
    Erstellt den konfigurierten Ausgabeordner falls er nicht existiert.
    
    :returns: Pfad zum Ausgabeordner
    :rtype: str
    """
    output_dir: str = CONFIG.PROJEKT_ANALYSE['OUTPUT_DIR']
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    return output_dir


def hauptfunktion(startverzeichnis: Optional[str] = None) -> None:
    """
    Führt die komplette Projekt-Analyse durch.
    
    Schritte:
    1. Findet alle Python-Dateien
    2. Analysiert die Import-Abhängigkeiten  
    3. Gibt verwendete und nicht verwendete Module aus
    4. Speichert Ergebnisse in konfigurierten Ausgabeordner
    5. Führt optionale Flake8-Prüfung durch

    :param startverzeichnis: Startverzeichnis für die Analyse
    :type startverzeichnis: Optional[str]
    :returns: None
    :rtype: None
    """
    if startverzeichnis is None:
        startverzeichnis = CONFIG.PROJEKT_PFAD
        
    # Type-Safety: startverzeichnis ist jetzt garantiert str
    assert startverzeichnis is not None, "Startverzeichnis nicht None"
    projekt_pfad: str = startverzeichnis
        
    print(f"🔍 Analyse im Projektordner: {projekt_pfad}\n")

    # Ausgabeordner vorbereiten
    output_dir: str = erstelle_ausgabeordner()
    output_filename: str = CONFIG.PROJEKT_ANALYSE['OUTPUT_FILENAME']
    output_path: str = os.path.join(output_dir, output_filename)
    
    # Alle Python-Dateien im Projekt finden
    py_dateien: List[str] = finde_python_dateien(projekt_pfad)
    
    # Importbeziehungen analysieren
    alle_module, verwendet_von, nicht_genutzt = analysiere_imports(py_dateien)

    # Ausgabe der gefundenen Dateien (Konsole)
    module_width: int = CONFIG.PROJEKT_ANALYSE['MODULE_NAME_WIDTH']
    
    print("📄 Gefundene Python-Dateien:")
    for modul, pfad in alle_module.items():
        print(f"  {modul:<{module_width}} → {pfad}")

    # Ausgabe der verwendeten Module (Konsole)
    print("\n🔗 Importierte Module (aus Projekt):")
    for modul, verwendet_durch in verwendet_von.items():
        print(f"  {modul:<{module_width}} verwendet in:")
        for nutzer in verwendet_durch:
            print(f"     └── {os.path.basename(nutzer)}")

    # Ausgabe der nicht verwendeten Dateien (Konsole)
    print("\n🧹 Nicht verwendete .py-Dateien:")
    for pfad in nicht_genutzt:
        print(f"  ❌ {pfad}")

    # Schreibe den vollständigen Verzeichnisbaum in die Ergebnisdatei
    schreibe_kompletten_verzeichnisbaum(output_path, projekt_pfad)

    # Ergebnisse in Datei speichern (weitere Details)
    encoding: str = CONFIG.PROJEKT_ANALYSE['FILE_ENCODING']
    
    with open(output_path, "a", encoding=encoding) as f:
        f.write("\n🔗 Verwendete Module:\n")
        for modul, verwendet_durch in verwendet_von.items():
            f.write(f"{modul} verwendet in:\n")
            for nutzer in verwendet_durch:
                f.write(f"  └── {os.path.basename(nutzer)}\n")
        f.write("\n🧹 Nicht verwendete Dateien:\n")
        for pfad in nicht_genutzt:
            f.write(f"❌ {pfad}\n")

    # Baumdarstellung der Modulabhängigkeiten (Konsolenausgabe)
    print_verwendete_module(verwendet_von)

    # Flake8-Analyse durchführen (optional)
    flake8_pruefen(py_dateien)
    
    # Externe Libraries analysieren
    externe_libs = analysiere_externe_libraries(py_dateien, alle_module)
    
    # Externe Libraries ausgeben (Konsole)
    print_externe_libraries(externe_libs)
    
    # Schreibe Analyse der externen Libraries in die Ausgabedatei
    schreibe_library_analyse(externe_libs, output_path)
    
    print("\n✅ Analyse abgeschlossen.")
    print(f"📁 Ergebnisse gespeichert in: {output_path}")


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
    print(f"📊 Starte umfassende Analyse des Projekts: {CONFIG.PROJEKT_ANALYSE.projekt_name}")
    print(f"📁 Basis-Verzeichnis: {CONFIG.PROJECT_ROOT}")
    print("=" * CONFIG.PROJEKT_ANALYSE.trennzeichen_laenge)
    
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
    schreibe_library_analyse(externe_libs, 
                             os.path.join(CONFIG.DATA_PATHS.fertig, 'externe_libraries.txt'))
    
    print(f"\n✅ Analyse abgeschlossen! Berichte gespeichert in: {CONFIG.DATA_PATHS.fertig}")
    print("=" * CONFIG.PROJEKT_ANALYSE.trennzeichen_laenge)


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
    
    for root, dirs, files in os.walk(CONFIG.PROJECT_ROOT):
        # Überspringe bestimmte Verzeichnisse
        dirs[:] = [d for d in dirs if d not in CONFIG.PROJEKT_ANALYSE.ignorierte_ordner]
        
        for file in files:
            if file.endswith(CONFIG.PROJEKT_ANALYSE.python_datei_endung):
                py_dateien.append(os.path.join(root, file))
    
    return py_dateien


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
        code_anteil = (statistiken['code_zeilen'] / statistiken['gesamt_zeilen']) * 100
        kommentar_anteil = (statistiken['kommentar_zeilen'] / statistiken['gesamt_zeilen']) * 100
        print(f"   📊 Code-Anteil: {code_anteil:.1f}%")
        print(f"   📊 Kommentar-Anteil: {kommentar_anteil:.1f}%")


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
            if any(import_name in os.path.basename(py_datei) for py_datei in py_dateien):
                abhängigkeiten[datei_name].append(import_name)
    
    return abhängigkeiten


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
    output_path = os.path.join(CONFIG.DATA_PATHS.fertig, 'code_statistiken.txt')
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"Code-Statistiken für {CONFIG.PROJEKT_ANALYSE.projekt_name}\n")
        f.write("=" * CONFIG.PROJEKT_ANALYSE.trennzeichen_laenge + "\n\n")
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
    output_path = os.path.join(CONFIG.DATA_PATHS.fertig, 'abhängigkeiten.txt')
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"Modul-Abhängigkeiten für {CONFIG.PROJEKT_ANALYSE.projekt_name}\n")
        f.write("=" * CONFIG.PROJEKT_ANALYSE.trennzeichen_laenge + "\n\n")
        f.write(f"Analyse-Zeitpunkt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        for modul, deps in abhängigkeiten.items():
            f.write(f"{modul}:\n")
            if deps:
                for dep in deps:
                    f.write(f"  → {dep}\n")
            else:
                f.write("  → (keine internen Abhängigkeiten)\n")
            f.write("\n")


if __name__ == "__main__":
    # Führe die neue umfassende Analyse durch
    neue_hauptfunktion()
