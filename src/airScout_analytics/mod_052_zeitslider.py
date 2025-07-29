"""
006_Umweltkontrollsystem – watchkido
analysis.py

Funktionen zur Datenanalyse.
Hier werden Analysefunktionen, Statistiken und Modelle implementiert.
"""

# === Imports ===
import os
import sys
import glob
import time
import pandas as pd
import matplotlib.pyplot as plt
import folium
import plotly.graph_objects as go
from selenium import webdriver
from PIL import Image
from folium.plugins import TimestampedGeoJson
from folium.plugins import MarkerCluster
from matplotlib.backends.backend_pdf import PdfPages
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=Warning)

# Für Bodenfläche im 3D-Plot
import numpy as np
# === Projektkontext vorbereiten ===
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import airScout_analytics.context as context
from config import CONFIG
from pyproj import Transformer

# === Plot-Funktionen ===

def plot_zeitslider(df, ergebnisse_dir, unterordner, filename_ohne_ext):
    """
    Erstellt eine zeitsensitive Geo-Karte mit Zeitschieberegler (Folium).
    """
    sensoren = [
        'Temperature_DHT_C', 'Humidity_RH', 'Light_Level', 'Light_Percent', 'GPS_Sats',
        'MQ2', 'MQ3', 'MQ4', 'MQ5', 'MQ6', 'MQ7', 'MQ8', 'MQ9', 'MQ135', 'Radiation_CPS'
    ]
    sensor_gas = {
        'MQ2': 'Methan, Butan, LPG, Rauch',
        'MQ3': 'Alkohol, Ethanol',
        'MQ4': 'Methan, CNG',
        'MQ5': 'Erdgas, LPG',
        'MQ6': 'LPG, Butan',
        'MQ7': 'Kohlenmonoxid (CO)',
        'MQ8': 'Wasserstoff (H₂)',
        'MQ9': 'CO, entflammbare Gase',
        'MQ135': 'Luftqualität (CO₂, NH₃, NOx)',
        'Temperature_DHT_C': 'Temperatur',
        'Humidity_RH': 'Luftfeuchte',
        'Light_Level': 'Lichtstärke',
        'Light_Percent': 'Licht [%]',
        'GPS_Sats': 'Satelliten',
        'Radiation_CPS': 'Strahlung (CPS)'
    }
    for sensor in sensoren:
        if sensor not in df.columns:
            print(f"Sensor '{sensor}' nicht in DataFrame, überspringe.")
            continue
        df_s = df[['GPS_Lat', 'GPS_Lon', 'DateTime', sensor]].dropna()
        df_s = df_s[df_s[sensor] > 0]
        if df_s.empty:
            print(f"Keine Daten für Sensor '{sensor}', überspringe.")
            continue
        df_s['DateTime'] = pd.to_datetime(df_s['DateTime'], errors='coerce')
        min_val = df_s[sensor].min()
        max_val = df_s[sensor].max()
        if max_val > min_val:
            df_s['value_scaled'] = (df_s[sensor] - min_val) / (max_val - min_val)
        else:
            df_s['value_scaled'] = 0.5

        features = []
        for _, row in df_s.iterrows():
            if pd.isna(row['DateTime']):
                continue
            v = row["value_scaled"]
            if v <= 0.5:
                r = int(2 * v * 255)
                g = 255
                b = 0
            else:
                r = 255
                g = int(255 - 2 * (v - 0.5) * 255)
                b = 0
            fill_color = f'#{r:02x}{g:02x}{b:02x}'
            feature = {
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [row['GPS_Lon'], row['GPS_Lat']],
                },
                'properties': {
                    'time': row['DateTime'].isoformat(),
                    'style': {'color': fill_color},
                    'icon': 'circle',
                    'iconstyle': {
                        'fillColor': fill_color,
                        'fillOpacity': 0.8,
                        'stroke': False,
                        'radius': 6
                    },
                    'popup': f"{sensor}: {row[sensor]:.2f}"
                }
            }
            features.append(feature)

        geojson = {'type': 'FeatureCollection', 'features': features}
        map_center = [df_s['GPS_Lat'].mean(), df_s['GPS_Lon'].mean()]
        m = folium.Map(location=map_center, zoom_start=14)
        TimestampedGeoJson(
            geojson,
            transition_time=200,
            period='PT5S',
            add_last_point=True,
            auto_play=False,
            loop=False
        ).add_to(m)
        os.makedirs(unterordner, exist_ok=True)
        gasinfo = sensor_gas.get(sensor, "")
        legend_html = f'''
        <div style="position: fixed; bottom: 50px; left: 50px; width: 440px; min-height: 60px; background-color: white; z-index:9999; font-size:13px; border:1px solid #bbb; border-radius:8px; padding:8px;">
            <b>Farbskala: {sensor} ({gasinfo})</b><br>
            <span style="float:left">{min_val:.2f}</span>
            <span style="float:right">{max_val:.2f}</span>
            <div style="clear:both;"></div>
            <div style="height: 16px; background: linear-gradient(to right, #00ff00 0%, #ffff00 50%, #ff0000 100%); border:1px solid #bbb;"></div>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        out_path = os.path.join(unterordner, f"{filename_ohne_ext}_Zeitslider_{sensor}.html")
        m.save(out_path)
        print(f"✅ Zeitslider gespeichert: {out_path}")


# === Platzhalterfunktion ===

    """
    Erstellt einen interaktiven 3D-Scatterplot mit Plotly (Longitude, Latitude, Höhe, Temperatur).
    """
    # Spaltennamen anpassen, falls nötig
    x_col = 'GPS_Lon' if 'GPS_Lon' in df.columns else 'lon'
    y_col = 'GPS_Lat' if 'GPS_Lat' in df.columns else 'lat'
    z_col = 'Höhe' if 'Höhe' in df.columns else ('hoehe' if 'hoehe' in df.columns else 'z')
    color_col = 'Temperature_DHT_C' if 'Temperature_DHT_C' in df.columns else ('temperatur' if 'temperatur' in df.columns else None)

    if not all(col in df.columns for col in [x_col, y_col, z_col]) or color_col is None:
        print("⚠️ 3D-Plot: Benötigte Spalten nicht gefunden. Überspringe plot_3d.")
        return

    fig = go.Figure(data=[go.Scatter3d(
        x=df[x_col],
        y=df[y_col],
        z=df[z_col],
        mode='markers',
        marker=dict(
            size=4,
            color=df[color_col],  # Farbcodierung nach Temperatur
            colorscale='Viridis',
            opacity=0.8
        )
    )])

    fig.update_layout(scene=dict(
        xaxis_title=x_col,
        yaxis_title=y_col,
        zaxis_title=z_col
    ))

    # Optional: Plot als HTML speichern
    html_path = os.path.join(unterordner, f"{filename_ohne_ext}_3dplot.html")
    fig.write_html(html_path)
    print(f"✅ 3D-Plot gespeichert: {html_path}")
    # fig.show()  # Nur für interaktive Sessions



# === Zentrale Plot-Sammlung ===
def erstelle_plots(df, filename_ohne_ext):
    """
    Erstellt alle gewünschten Diagramme für die Analyse.
    """
    ergebnisse_dir = os.path.join("data", "ergebnisse")
    unterordner = os.path.join(ergebnisse_dir, filename_ohne_ext)
    os.makedirs(ergebnisse_dir, exist_ok=True)
    os.makedirs(unterordner, exist_ok=True)

    plotfunktionen = [

        plot_zeitslider,

        # ... bis zu 40 weitere Plotfunktionen ...
    ]

    for plot_func in plotfunktionen:
        try:
            plot_func(df, ergebnisse_dir, unterordner, filename_ohne_ext)
        except Exception as e:
            print(f"Warnung: Fehler in {plot_func.__name__}: {e}")


# === Main Plotting Funktion ===
def main_plotting(filename_ohne_ext=None, df=None):
    """
    Hauptfunktion für den Pipeline-Aufruf. Lädt DataFrame (falls nötig) und erstellt alle Plots.
    """
    # Immer die erste CSV aus 'data/bearbeitet3' verwenden
    from airScout_analytics import context
    bearbeitet3_ordner = os.path.join("data", "bearbeitet3")
    suchmuster = os.path.join(bearbeitet3_ordner, "*.csv")
    treffer = glob.glob(suchmuster)
    if not treffer:
        raise FileNotFoundError(
            f"Keine CSV-Datei gefunden im Ordner: {bearbeitet3_ordner}")
    pfad = treffer[0]
    # Ordnername und Plots werden aus context.filename_ohne_ext gebildet
    df = pd.read_csv(pfad)

    erstelle_plots(df, context.filename_ohne_ext)


# === Einstiegspunkt ===
def main():
    """
    Pipeline-kompatibler Einstiegspunkt: Führt main_plotting() aus.
    """
    return main_plotting()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Fehler beim Plotten: {e}")
