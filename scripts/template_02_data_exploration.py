import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def explore_data(df):
    # Anzeigen grundlegender statistischer Informationen
    print("Deskriptive Statistik:")
    print(df.describe())

    # Anzeigen der ersten Zeilen des DataFrames
    print("\nErste 5 Zeilen des Datensatzes:")
    print(df.head())

    # Verteilung von numerischen Features
    print("\nHistogramme der numerischen Features:")
    df.hist(bins=30, figsize=(10, 10))
    plt.show()

    # Korrelationsmatrix
    print("\nKorrelationsmatrix:")
    corr = df.corr()
    sns.heatmap(corr, annot=True, cmap="coolwarm")
    plt.show()

    # Fehlende Werte
    print("\nFehlende Werte:")
    print(df.isnull().sum())

if __name__ == "__main__":
    # Beispiel: CSV-Datei laden und analysieren
    df = pd.read_csv('path_to_data.csv')
    explore_data(df)
