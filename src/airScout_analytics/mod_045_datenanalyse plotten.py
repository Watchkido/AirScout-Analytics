"""
006_Umweltkontrollsystem  watchkido
analysis.py
Funktionen zur Datenanalyse.
Hier werden Analysefunktionen, Statistiken und Modelle implementiert.
"""
# module/040_datenanalyse_plotten.py
from config import CONFIG
import matplotlib.pyplot as plt
import os

def erstelle_plots(df):
    os.makedirs("plots", exist_ok=True)

    plt.figure()
    df['Temperature_DHT_C'].plot(title='Temperaturverlauf')
    plt.savefig("plots/temperaturverlauf.png")
    plt.close()

    plt.figure()
    df['MQ7'].plot(title='CO-Wert (MQ7)')
    plt.axhline(500, color='red', linestyle='--', label='Warnschwelle')
    plt.legend()
    plt.savefig("plots/co_verlauf.png")
    plt.close()

        
if __name__ == "__main__":
    # Code hier drunter wird nur ausgeführt wenn das Skript direkt aufgerufen wird
    pass