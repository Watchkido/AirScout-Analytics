import pandas as pd
import numpy as np

def detect_outliers(df):
    # Berechnung der IQR (Interquartilsabstand)
    Q1 = df.quantile(0.25)
    Q3 = df.quantile(0.75)
    IQR = Q3 - Q1
    outliers = ((df < (Q1 - 1.5 * IQR)) | (df > (Q3 + 1.5 * IQR)))
    return outliers

if __name__ == "__main__":
    # Beispiel: CSV-Datei laden und Ausreißer erkennen
    df = pd.read_csv('path_to_data.csv')
    outliers = detect_outliers(df)
    print(outliers)
