"""
AirScout-Analytics Pipeline-Steuerung
-------------------------------------

Dieses Skript steuert die Ausführung aller Pipeline-Module im Projekt.
Damit ein Modul automatisch ausgeführt wird, müssen folgende Bedingungen erfüllt sein:

- Die Datei liegt im gleichen Verzeichnis wie diese Pipeline und beginnt mit 'mod_' und endet auf '.py'.
- Die Datei darf nicht 'mod_000_pipeline.py' heißen (diese wird übersprungen).
- Das Modul muss eine Funktion 'main' enthalten (def main(): ...), die keine Argumente erwartet.
- Nur dann wird das Modul importiert und seine main()-Funktion ausgeführt.
- Gibt es keine main()-Funktion, wird das Modul übersprungen.
- Bei einem Fehler im Modul wird die Pipeline abgebrochen.


Jedes Modul ist für einen klar abgegrenzten Verarbeitungsschritt zuständig (Laden, Analyse, Feature Engineering, Visualisierung, Reporting etc.).
Die Pipeline ist so konzipiert, dass sie leicht um weitere Module erweitert werden kann.
"""


from config import CONFIG
from mod_010_laden_reinigen import laden_und_reinigen
from mod_020_csv_analyzer import csv_info_extractor

def main():
    import glob
    import os
    import importlib
    import sys

    # Verzeichnis mit den Modulen
    modulverzeichnis = os.path.dirname(os.path.abspath(__file__))
    # Alle mod_*.py Dateien (außer pipeline selbst) sortiert laden
    alle_module = sorted([
        f for f in os.listdir(modulverzeichnis)
        if f.startswith("mod_") and f.endswith(".py") and f != "mod_000_pipeline.py"
    ])

    print("Starte sequentielle Pipeline:")
    for modulname in alle_module:
        modulpfad = os.path.join(modulverzeichnis, modulname)
        print(f"\n--- Starte Modul: {modulname} ---")
        # Dynamisch importieren
        modname = modulname[:-3]
        try:
            mod = importlib.import_module(modname)
            # Wenn main()-Funktion vorhanden, ausführen
            if hasattr(mod, "main"):
                result = mod.main()
                print(f"Modul {modulname} erfolgreich ausgeführt. Rückgabewert: {result}")
            else:
                print(f"Kein main() in {modulname}, überspringe Ausführung.")
        except Exception as e:
            print(f"Fehler beim Ausführen von {modulname}: {e}")
            break
    print('\nPipeline vollständig abgeschlossen.')

if __name__ == "__main__":
    main()