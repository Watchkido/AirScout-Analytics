"""
data_processing.py
Skript zur Datenverarbeitung.
Hier werden Rohdaten eingelesen, verarbeitet und gespeichert.
"""

import pandas as pd

def process_data(input_file, output_file):
    df = pd.read_csv(input_file)
    # Beispielhafte Verarbeitung: Duplizieren der Daten
    df = pd.concat([df, df])
    df.to_csv(output_file, index=False)
    print(f'Daten verarbeitet und in {output_file} gespeichert.')

if __name__ == '__main__':
    process_data('data/raw/input.csv', 'data/processed/output.csv')
