
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

# === CSV laden aus bearbeitet2 ===
if not hasattr(context, 'filename_ohne_ext') or context.filename_ohne_ext is None:
    raise ValueError("context.filename_ohne_ext ist nicht gesetzt!")
suchmuster = os.path.join("data", "bearbeitet2", f"*{context.filename_ohne_ext}*.csv")
treffer = glob.glob(suchmuster)
if not treffer:
    raise FileNotFoundError(f"Keine Datei gefunden mit Muster: {suchmuster}")
if len(treffer) > 1:
    print(f"Warnung: Mehrere Dateien gefunden, verwende die erste: {treffer[0]}")
pfad = treffer[0]
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
filename_ohne_ext = context.filename_ohne_ext
ergebnisse_dir = os.path.join("data", "ergebnisse")
unterordner = os.path.join(ergebnisse_dir, filename_ohne_ext)
os.makedirs(ergebnisse_dir, exist_ok=True)
os.makedirs(unterordner, exist_ok=True)

pfad1 = os.path.join(ergebnisse_dir, f"karte_mq135_{filename_ohne_ext}.png")
pfad2 = os.path.join(unterordner, f"{filename_ohne_ext}_karte_mq135.png")
plt.savefig(pfad1)
plt.savefig(pfad2)
plt.show()
