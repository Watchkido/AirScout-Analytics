"""
006_Umweltkontrollsystem  watchkido
visualization.py
Funktionen zur Visualisierung von Daten.
Hier werden Plots und Diagramme erstellt.
"""
from config import CONFIG
import matplotlib.pyplot as plt

def plot_hist(df, column):
    df[column].hist()
    plt.show()

if __name__ == "__main__":
# Code hier drunter wird nur ausgeführt wenn das Skript direkt aufgerufen wird



---------------------------------------------------------------
 #Ziel: Filtern nach Stunde, Ort, Höhe, Temperatur, Lichtstärke usw.
🔧 1. Daten einlesen und vorbereiten
python
Kopieren
Bearbeiten
import pandas as pd

df = pd.read_csv("deine_daten.csv")  # oder .xlsx einlesen

# Datum und Uhrzeit kombinieren und in datetime umwandeln
df['timestamp'] = pd.to_datetime(df['datum'] + ' ' + df['uhrzeit'])

# Neue Spalten zur Analyse
df['Stunde'] = df['timestamp'].dt.hour
df['Tag'] = df['timestamp'].dt.date

----------------------------------------------------------------
 #2. Einfaches Diagramm filtern nach Stunde und Ort (mit Matplotlib)

import matplotlib.pyplot as plt

# Beispiel: Zeige Temperatur für einen bestimmten Ort und bestimmte Stunde
ort = "Küche"
stunde = 14

gefiltert = df[(df['Ort'] == ort) & (df['Stunde'] == stunde)]

plt.figure(figsize=(10, 5))
plt.plot(gefiltert['timestamp'], gefiltert['Temperatur'], label=f"{ort} um {stunde} Uhr")
plt.xlabel("Zeit")
plt.ylabel("Temperatur")
plt.legend()
plt.grid()
plt.show()



----------------------------------------------------------------------