"""
data_loader.py
Modul zum Laden von Daten aus einer CSV-Datei.
Hier werden Funktionen bereitgestellt, um CSV-Daten komfortabel einzulesen.
"""

import csv
from typing import List, Dict

def lade_csv_daten(dateipfad: str, delimiter: str = ",") -> List[Dict[str, str]]:
    """
    Lädt Daten aus einer CSV-Datei und gibt sie als Liste von Dictionaries zurück.

    :param dateipfad: Pfad zur CSV-Datei.
    :type dateipfad: str
    :param delimiter: Trennzeichen der CSV-Datei (Standard: ',').
    :type delimiter: str
    :returns: Liste von Zeilen als Dictionaries (Spaltenname -> Wert).
    :rtype: List[Dict[str, str]]
    :raises FileNotFoundError: Wenn die Datei nicht gefunden wurde.
    :raises csv.Error: Bei Fehlern im CSV-Format.
    :example:

        >>> daten = lade_csv_daten("daten.csv")
        >>> print(daten[0])
        {'Name': 'Max', 'Alter': '23'}
    """
    daten = []
    try:
        with open(dateipfad, mode="r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile, delimiter=delimiter)
            for zeile in reader:
                daten.append(dict(zeile))
    except FileNotFoundError:
        raise FileNotFoundError(f"Datei nicht gefunden: {dateipfad}")
    except csv.Error as e:
        raise csv.Error(f"Fehler beim Lesen der CSV-Datei: {e}")
    return daten

# TODO: Funktion zum Schreiben von Daten in eine CSV-


import pandas as pd

def load_data(file_path):
    df = pd.read_csv(file_path)
    return df

if __name__ == "__main__":
    df = load_data('path_to_data.csv')
    print(df.head())
