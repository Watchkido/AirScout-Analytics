"""
modul1.py
Beispiel-Modul 1.
Hier können Funktionen oder Klassen für Modul 1 implementiert werden.
"""


from config import CONFIG
from mod_010_laden_reinigen import laden_und_reinigen
from mod_020_csv_analyzer import csv_info_extractor

def main():
    # Daten laden und reinigen (liefert Pfad zur bereinigten Datei)
    bereinigte_datei = laden_und_reinigen()
    # Analyse der bereinigten Datei durchführen
    # Robust prüfen, ob ein gültiger Dateipfad zurückgegeben wurde
    if bereinigte_datei is not None and isinstance(bereinigte_datei, str) and bereinigte_datei != '':
        info_txt = csv_info_extractor(bereinigte_datei)
        print(f'Analyse abgeschlossen: {info_txt}')
    else:
        print('Keine bereinigte Datei gefunden – Analyse übersprungen.')
    print('Pipeline erfolgreich ausgeführt.')

if __name__ == "__main__":
    main()