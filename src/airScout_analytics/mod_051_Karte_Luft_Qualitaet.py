

"""
Modul zur Erstellung einer interpolierten Luftqualitätskarte (MQ135) auf Basis von GPS-Daten.

Dieses Modul wird von der Pipeline automatisch aufgerufen, sofern eine main()-Funktion vorhanden ist.
Die Karte wird als PNG in den Ergebnisordnern gespeichert.
"""

import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from scipy.interpolate import griddata
import numpy as np
import os
import glob
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import airScout_analytics.context as context
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=Warning)


def main() -> None:
    """
    Erstellt eine interpolierte Luftqualitätskarte (MQ135) und speichert sie als PNG.

    :raises ValueError: Wenn context.filename_ohne_ext nicht gesetzt ist.
    :raises FileNotFoundError: Wenn keine passende CSV-Datei gefunden wird.
    """
    # Immer die erste CSV aus 'data/bearbeitet3' verwenden
    bearbeitet3_ordner = os.path.join("data", "bearbeitet3")
    suchmuster = os.path.join(bearbeitet3_ordner, "*.csv")
    treffer = glob.glob(suchmuster)
    if not treffer:
        raise FileNotFoundError(
            f"Keine CSV-Datei gefunden im Ordner: {bearbeitet3_ordner}")
    pfad = treffer[0]
    # Ordnername und Plots werden aus context.filename_ohne_ext gebildet
    df = pd.read_csv(pfad)
    df = df.dropna(subset=['GPS_Lat', 'GPS_Lon', 'MQ135'])

    # === Daten extrahieren ===
    lats = df['GPS_Lat'].values
    lons = df['GPS_Lon'].values
    values = df['MQ135'].values  # z.B. MQ135 (Luftqualität)

    # === Gitter zur Interpolation ===
    lon_grid = np.linspace(lons.min(), lons.max(), 200)
    lat_grid = np.linspace(lats.min(), lats.max(), 200)
    lon_mesh, lat_mesh = np.meshgrid(lon_grid, lat_grid)

    # === Interpolation (z.B. IDW oder linear) ===
    grid_values = griddata((lons, lats), values, (lon_mesh, lat_mesh), method='linear')

    # === Karte zeichnen ===
    fig = plt.figure(figsize=(10, 10))
    ax = plt.axes(projection=ccrs.PlateCarree())

    # Kartenfeatures
    ax.add_feature(cfeature.BORDERS, linestyle=':', alpha=0.5)
    ax.add_feature(cfeature.COASTLINE, alpha=0.3)
    ax.add_feature(cfeature.LAND, edgecolor='black', alpha=0.1)
    ax.set_extent([lons.min() - 0.01, lons.max() + 0.01,
                   lats.min() - 0.01, lats.max() + 0.01], crs=ccrs.PlateCarree())

    # Farbkarte
    cf = ax.contourf(lon_mesh, lat_mesh, grid_values,
                     levels=np.linspace(values.min(), values.max(), 100),
                     cmap='plasma', alpha=0.7)

    # Farbleiste
    cbar = plt.colorbar(cf, orientation='horizontal', pad=0.05)
    cbar.set_label('MQ135 (Luftqualität in Rohwerten)')

    # Punkte anzeigen
    ax.scatter(lons, lats, color='black', s=5, alpha=0.5, label='Messpunkte')
    plt.title('Luftqualität MQ135 – Prognosekarte')
    plt.legend()

    # === Speichern als PNG in ergebnisse und Unterordner ===
    ergebnisse_dir = os.path.join("data", "ergebnisse")
    unterordner = os.path.join(ergebnisse_dir, context.filename_ohne_ext)
    os.makedirs(ergebnisse_dir, exist_ok=True)
    os.makedirs(unterordner, exist_ok=True)

    pfad1 = os.path.join(ergebnisse_dir, f"karte_mq135_{context.filename_ohne_ext}.png")
    pfad2 = os.path.join(unterordner, f"{context.filename_ohne_ext}_karte_mq135.png")
    plt.savefig(pfad1)
    plt.savefig(pfad2)
    plt.show()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Fehler beim Erstellen der Luftqualitätskarte: {e}")

