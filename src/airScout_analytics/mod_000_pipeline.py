
"""
AirScout-Analytics Pipeline-Steuerung
-------------------------------------

Dieses Skript steuert die Ausführung aller Pipeline-Module im Projekt.

Bedingungen für die automatische Ausführung eines Moduls:
    - Die Datei liegt im gleichen Verzeichnis wie diese Pipeline und beginnt mit 'mod_' und endet auf '.py'.
    - Die Datei darf nicht 'mod_000_pipeline.py' heißen (diese wird übersprungen).
    - Das Modul muss eine Funktion 'main' enthalten (def main(): ...), die keine Argumente erwartet.
    - Nur dann wird das Modul importiert und seine main()-Funktion ausgeführt.
    - Gibt es keine main()-Funktion, wird das Modul übersprungen.
    - Bei einem Fehler im Modul wird die Pipeline abgebrochen.


Jedes Modul ist für einen klar abgegrenzten Verarbeitungsschritt zuständig (Laden, Analyse, Feature Engineering, Visualisierung, Reporting etc.).
Die Pipeline ist so konzipiert, dass sie leicht um weitere Module erweitert werden kann.
"""


import os
import importlib
import time
import shutil
try:
    import context
except ImportError:
    context = None
try:
    from config import CONFIG
except ImportError:
    CONFIG = None
from mod_010_laden_reinigen import laden_und_reinigen
from mod_020_csv_analyzer import csv_info_extractor

def main():

    modulverzeichnis = os.path.dirname(os.path.abspath(__file__))
    # Alle mod_*.py Dateien (außer pipeline selbst) sortiert laden
    alle_module = sorted([
        f for f in os.listdir(modulverzeichnis)
        if f.startswith("mod_") and f.endswith(".py") and f != "mod_000_pipeline.py"
    ])

    print("Starte sequentielle Pipeline:")

    for modulname in alle_module:
        time.sleep(3)
        modulpfad = os.path.join(modulverzeichnis, modulname)
        print(f"\n--- Starte Modul: {modulname} ---")
        modname = modulname[:-3]
        try:
            mod = importlib.import_module(modname)
            if hasattr(mod, "main"):
                result = mod.main()
                print(f"Modul {modulname} erfolgreich ausgeführt. Rückgabewert: {result}")
            else:
                print(f"Kein main() in {modulname}, überspringe Ausführung.")
        except Exception as e:
            print(f"Fehler beim Ausführen von {modulname}: {e}")
            print(f"[Warnung] Modul {modulname} wurde übersprungen. Weiter mit dem nächsten Modul.")

    print("\nPipeline vollständig abgeschlossen.")





    # Am Ende: Nur die gerade bearbeiteten Dateien in den Zielordnern löschen
    # DATA_ROOT bleibt aus CONFIG, Namenszusatz aus context
    filename_ohne_ext = getattr(context, "filename_ohne_ext", None) if context else None
    zu_loeschende_ordner = [
        os.path.join(CONFIG.DATA_ROOT, "bearbeitet"),
        os.path.join(CONFIG.DATA_ROOT, "bearbeitet1"),
        os.path.join(CONFIG.DATA_ROOT, "bearbeitet2"),
        os.path.join(CONFIG.DATA_ROOT, "ergebnisse3"),
    ]
    # TODO: Liste der bearbeiteten Dateien aus den Modulen holen!
    bearbeitete_dateien = []  # z.B. als Rückgabe der Module oder als globale Variable
    if not filename_ohne_ext:
        print("[Warnung] Kein Namensbestandteil für Löschprüfung gefunden (context.filename_ohne_ext)")
    # Zielordner für Kopien vor dem Löschen
    kopierziel = os.path.join(CONFIG.DATA_ROOT, "ergebnisse", filename_ohne_ext)
    if not os.path.isdir(kopierziel):
        try:
            os.makedirs(kopierziel)
            print(f"Kopierziel erstellt: {kopierziel}")
        except Exception as e:
            print(f"Fehler beim Erstellen des Kopierziels: {e}")
    import shutil
    for ordner in zu_loeschende_ordner:
        if not os.path.isdir(ordner):
            continue
        for datei in bearbeitete_dateien:
            if filename_ohne_ext and filename_ohne_ext not in datei:
                print(f"Überspringe Datei (Namensbestandteil fehlt): {datei}")
                continue
            pfad = os.path.join(ordner, datei)
            if os.path.isfile(pfad):
                # Vor dem Löschen kopieren
                try:
                    shutil.copy2(pfad, kopierziel)
                    print(f"Datei kopiert nach: {kopierziel}")
                except Exception as e:
                    print(f"Fehler beim Kopieren von {pfad} nach {kopierziel}: {e}")
                # Dann löschen
                try:
                    os.remove(pfad)
                    print(f"Datei gelöscht: {pfad}")
                except Exception as e:
                    print(f"Fehler beim Löschen von {pfad}: {e}")


# am ende der pipeline sollen die gerade bearbeiteten dateien in 
# 1. data\bearbeitet
# 2. data\bearbeitet1
# 3. data\bearbeitet2
# 4. data\ergebnisse3
#gelöscht werden. aber nur diese! keine anderen!
    




if __name__ == "__main__":
    main()