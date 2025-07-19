import pandas as pd

def generate_report(df):
    # Basisbericht
    print("Datenbericht:")
    print(f"Anzahl der Zeilen: {len(df)}")
    print(f"Anzahl der Spalten: {len(df.columns)}")
    print("\nDeskriptive Statistik:")
    print(df.describe())

    # Visualisierung der Verteilung (optional)
    df.hist(figsize=(10, 10))
    plt.show()

if __name__ == "__main__":
    # Beispiel: CSV-Datei laden und Bericht generieren
    df = pd.read_csv('path_to_data.csv')
    generate_report(df)

            
if __name__ == "__main__":
# Code hier drunter wird nur ausgeführt wenn das Skript direkt aufgerufen wird