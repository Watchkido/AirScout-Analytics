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
import pandas as pd
import matplotlib.pyplot as plt
import folium
from folium.plugins import TimestampedGeoJson
from folium.plugins import MarkerCluster
# === Projektkontext vorbereiten ===
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import airScout_analytics.context as context
from config import CONFIG


# === Plot-Funktionen ===

def plot_temperaturverlauf(df, ergebnisse_dir, unterordner, filename_ohne_ext):
    """
    Erstellt ein Liniendiagramm für den Temperaturverlauf.
    """
    plt.figure()
    df['Temperature_DHT_C'].plot(title='Temperaturverlauf')
    pfad1a = os.path.join(ergebnisse_dir, f"bild1_{filename_ohne_ext}.png")
    pfad1b = os.path.join(unterordner, f"{filename_ohne_ext}_bild1.png")
    plt.savefig(pfad1a)
    plt.savefig(pfad1b)
    plt.close()


def plot_co_verlauf(df, ergebnisse_dir, unterordner, filename_ohne_ext):
    """
    Erstellt ein Liniendiagramm für den CO-Wert (MQ7).
    """
    plt.figure()
    df['MQ7'].plot(title='CO-Wert (MQ7)')
    plt.axhline(500, color='red', linestyle='--', label='Warnschwelle')
    plt.legend()
    pfad2a = os.path.join(ergebnisse_dir, f"bild2_{filename_ohne_ext}.png")
    pfad2b = os.path.join(unterordner, f"{filename_ohne_ext}_bild2.png")
    plt.savefig(pfad2a)
    plt.savefig(pfad2b)
    plt.close()

def plot_mq2(df, ergebnisse_dir, unterordner, filename_ohne_ext):
    """
    Erstellt ein Liniendiagramm für MQ2.
    """
    plt.figure()
    df['MQ2'].plot(title='MQ2 Rauchgas')
    plt.ylabel('MQ2')
    pfad = os.path.join(ergebnisse_dir, f"mq2_" + filename_ohne_ext + ".png")
    plt.savefig(pfad)
    plt.close()

def plot_mq7(df, ergebnisse_dir, unterordner, filename_ohne_ext):
    """
    Erstellt ein Liniendiagramm für MQ7 Kohlenmonoxid.
    """
    plt.figure()
    df['MQ7'].plot(title='MQ7 Kohlenmonoxid')
    plt.axhline(500, color='red', linestyle='--', label='Warnschwelle')
    plt.legend()
    plt.ylabel('MQ7')
    pfad = os.path.join(ergebnisse_dir, f"mq7_" + filename_ohne_ext + ".png")
    plt.savefig(pfad)
    plt.close()

def plot_luftkarte(df, ergebnisse_dir, unterordner, filename_ohne_ext):
    
    # Nur Zeilen mit gültigen GPS-Daten verwenden
    df = df[(df['GPS_Lat'].notna()) & (df['GPS_Lon'].notna())]

    # === Mittelpunkt der Karte (Neustadt an der Weinstraße) ===
    map_center = [49.3477, 8.1399]
    sensor_map = folium.Map(location=map_center, zoom_start=13, control_scale=True)

    # === Farbskala für MQ135 Luftqualität ===
    def get_color(value):
        if value < 4000:
            return 'green'
        elif value < 8000:
            return 'orange'
        else:
            return 'red'

    # === MarkerCluster hinzufügen ===
    marker_cluster = MarkerCluster().add_to(sensor_map)

    for _, row in df.iterrows():
        lat, lon = row['GPS_Lat'], row['GPS_Lon']
        mq135 = row['MQ135_ugm3']
        
        popup_text = (
            f"<b>Datum:</b> {row['DateTime']}<br>"
            f"<b>Temperatur:</b> {row['Temperature_DHT_C']} °C<br>"
            f"<b>Luftfeuchte:</b> {row['Humidity_RH']} %<br>"
            f"<b>MQ135 Luftqualität:</b> {mq135} µg/m³<br>"
            f"<b>Radioaktivität:</b> {row['Radiation_CPS']} CPS"
        )
        
        folium.CircleMarker(
            location=(lat, lon),
            radius=5,
            color=get_color(mq135),
            fill=True,
            fill_color=get_color(mq135),
            fill_opacity=0.7,
            popup=folium.Popup(popup_text, max_width=300)
        ).add_to(marker_cluster)

    # === Farblegende als HTML-Overlay ===
    legend_html = '''
    <div style="position: fixed; bottom: 50px; left: 50px; width: 220px; height: 90px; background-color: white; z-index:9999; font-size:14px; border:1px solid #bbb; border-radius:8px; padding:8px;">
        <b>Farbskala: MQ135 Luftqualität</b><br>
        <div style="margin-top:6px;">
            <span style="display:inline-block;width:18px;height:18px;background:#00cc00;border:1px solid #bbb;"></span>
            <span style="margin-left:8px;">&lt; 4000 µg/m³ (gut)</span>
        </div>
        <div style="margin-top:4px;">
            <span style="display:inline-block;width:18px;height:18px;background:orange;border:1px solid #bbb;"></span>
            <span style="margin-left:8px;">4000–7999 µg/m³ (mittel)</span>
        </div>
        <div style="margin-top:4px;">
            <span style="display:inline-block;width:18px;height:18px;background:#cc0000;border:1px solid #bbb;"></span>
            <span style="margin-left:8px;">≥ 8000 µg/m³ (hoch)</span>
        </div>
    </div>
    '''
    sensor_map.get_root().html.add_child(folium.Element(legend_html))

    # === Karte als HTML speichern ===
    os.makedirs(unterordner, exist_ok=True)
    output_file = os.path.join(unterordner, f"punktluftwert_{filename_ohne_ext}.html")
    sensor_map.save(output_file)
    print(f"Karte gespeichert als: {output_file}")







def plot_zeitslider(df, ergebnisse_dir, unterordner, filename_ohne_ext):
    """
    Erstellt eine zeitsensitive Geo-Karte mit Zeitschieberegler (Folium).
    """
    sensor = 'MQ135'  # Sensor auswählen
    # Stelle sicher, dass DateTime als datetime vorliegt
    df = df[['GPS_Lat', 'GPS_Lon', 'DateTime', sensor]].dropna()
    df = df[df[sensor] > 0]
    df['DateTime'] = pd.to_datetime(df['DateTime'], errors='coerce')

    df['value_scaled'] = (df[sensor] - df[sensor].min()) / (df[sensor].max() - df[sensor].min())

    features = []
    for _, row in df.iterrows():
        # Nur Zeilen mit gültigem Timestamp verwenden
        if pd.isna(row['DateTime']):
            continue
        # Farbverlauf: niedrig = grün, mittel = gelb, hoch = rot
        # value_scaled: 0 = grün, 0.5 = gelb, 1 = rot
        v = row["value_scaled"]
        if v <= 0.5:
            # Übergang grün -> gelb
            r = int(2 * v * 255)
            g = 255
            b = 0
        else:
            # Übergang gelb -> rot
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
                'popup': f"{sensor}: {row[sensor]:.2f} µg/m³"
            }
        }
        features.append(feature)

    geojson = {'type': 'FeatureCollection', 'features': features}

    map_center = [df['GPS_Lat'].mean(), df['GPS_Lon'].mean()]
    m = folium.Map(location=map_center, zoom_start=14)

    TimestampedGeoJson(
        geojson,
        transition_time=200,
        period='PT5S',
        add_last_point=True,
        auto_play=False,
        loop=False
    ).add_to(m)

    # Stelle sicher, dass der Unterordner existiert
    os.makedirs(unterordner, exist_ok=True)

    # Farblegende als HTML hinzufügen (grün-gelb-rot)
    min_val = df[sensor].min()
    max_val = df[sensor].max()
    legend_html = f'''
    <div style="position: fixed; 
                bottom: 50px; left: 50px; width: 240px; height: 60px; 
                background-color: white; z-index:9999; font-size:14px; border:1px solid #bbb; border-radius:8px; padding:8px;">
        <b>Farbskala: {sensor}</b><br>
        <span style="float:left">{min_val:.2f}</span>
        <span style="float:right">{max_val:.2f}</span>
        <div style="clear:both;"></div>
        <div style="height: 16px; background: linear-gradient(to right, #00ff00 0%, #ffff00 50%, #ff0000 100%); border:1px solid #bbb;"></div>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))

    out_path = os.path.join(unterordner, f"{filename_ohne_ext}_zeitslider.html")
    m.save(out_path)


# === Platzhalterfunktion ===
def plot_beispiel_3(df, ergebnisse_dir, unterordner, filename_ohne_ext):
    """
    Platzhalter für weitere Diagrammarten.
    """
    pass  # TODO: Implementieren


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
        plot_temperaturverlauf,
        plot_co_verlauf,
        plot_zeitslider,
        plot_mq2,
        plot_mq7,
        plot_luftkarte
        # plot_beispiel_3,
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
    if filename_ohne_ext is None:
        if not hasattr(context, 'filename_ohne_ext') or context.filename_ohne_ext is None:
            raise ValueError("context.filename_ohne_ext ist nicht gesetzt!")
        filename_ohne_ext = context.filename_ohne_ext

    if df is None:
        suchmuster = os.path.join("data", "bearbeitet2", f"*{filename_ohne_ext}*.csv")
        treffer = glob.glob(suchmuster)
        if not treffer:
            raise FileNotFoundError(f"Keine Datei gefunden mit Muster: {suchmuster}")
        if len(treffer) > 1:
            print(f"Warnung: Mehrere Dateien gefunden, verwende die erste: {treffer[0]}")
        pfad = treffer[0]
        df = pd.read_csv(pfad)

    erstelle_plots(df, filename_ohne_ext)


# === Einstiegspunkt ===
def main():
    """
    Pipeline-kompatibler Einstiegspunkt: Führt main_plotting() aus.
    """
    return main_plotting()


if __name__ == "__main__":
    try:
        main_plotting()
    except Exception as e:
        print(f"Fehler beim Plotten: {e}")
