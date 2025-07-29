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
from folium.plugins import TimestampedGeoJson
from folium.plugins import MarkerCluster
from matplotlib.backends.backend_pdf import PdfPages
import warnings
import numpy as np
from pyproj import Transformer

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=Warning)

# === Projektkontext vorbereiten ===
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
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



def plot_zeitslider_lautstaerke(df, ergebnisse_dir, unterordner, filename_ohne_ext):
    """
    Erstellt eine zeitsensitive Lautstärke-Karte (Folium) basierend auf 'Mic2'.
    """
    sensor = 'Mic2'
    df = df[['GPS_Lat', 'GPS_Lon', 'DateTime', sensor]].dropna()
    df = df[df[sensor] >= 0]
    df['DateTime'] = pd.to_datetime(df['DateTime'], errors='coerce')

    features = []
    for _, row in df.iterrows():
        val = row[sensor]
        if val < 125:
            color = 'rgba(0,0,0,0)'
        elif val < 250:
            color = 'yellow'
        else:
            color = 'red'
        feature = {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [row['GPS_Lon'], row['GPS_Lat']],
            },
            'properties': {
                'time': row['DateTime'].isoformat(),
                'style': {'color': color},
                'icon': 'circle',
                'iconstyle': {
                    'fillColor': color,
                    'fillOpacity': 0.9,
                    'stroke': False,
                    'radius': 6
                },
                'popup': f"Lautstärke: {val:.1f}<br>Datum: {row['DateTime']}"
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
    # Legende (HTML-String, Zeilenlänge ignoriert)
    legend_html = '''
    <div style="position: fixed; bottom: 50px; left: 50px; width: 240px; background-color: white; z-index:9999; font-size:13px; border:1px solid #bbb; border-radius:8px; padding:8px;">
        <b>Farbskala: Lautstärke (Mic2)</b><br>
        <div style="margin-top:6px;">
            <span style="display:inline-block;width:18px;height:18px;background:green;border:1px solid #bbb;"></span>
            <span style="margin-left:8px;">0–124: Leise</span>
        </div>
        <div style="margin-top:4px;">
            <span style="display:inline-block;width:18px;height:18px;background:yellow;border:1px solid #bbb;"></span>
            <span style="margin-left:8px;">125–249: Mittel</span>
        </div>
        <div style="margin-top:4px;">
            <span style="display:inline-block;width:18px;height:18px;background:red;border:1px solid #bbb;"></span>
            <span style="margin-left:8px;">250–500: Laut</span>
        </div>
        <div style="margin-top:6px;font-size:11px;color:#555;">Frank Albrecht</div>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    os.makedirs(unterordner, exist_ok=True)
    html_path = os.path.join(unterordner, f"{filename_ohne_ext}_lautstaerke.html")
    png_path = os.path.join(unterordner, f"{filename_ohne_ext}_lautstaerke.png")
    m.save(html_path)
    print(f"✅ HTML gespeichert: {html_path}")
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--window-size=1600x1000')
        driver = webdriver.Chrome(options=options)
        driver.get("file://" + os.path.abspath(html_path))
        time.sleep(2)
        # Slider ans Ende setzen (JavaScript, Humor: Slider-Party am rechten Rand)
        script = """
        let sliders = document.getElementsByClassName('leaflet-control-timecontrol');
        if (sliders.length) {
            let input = sliders[0].querySelector('input[type=\"range\"]');
            if (input) input.value = input.max;
            let evt = new Event('input', { bubbles: true });
            input.dispatchEvent(evt);
        }
        """
        driver.execute_script(script)
        time.sleep(1)
        driver.save_screenshot(png_path)
        driver.quit()
        print(f"✅ PNG gespeichert (letzter Zeitschritt): {png_path}")
    except Exception as e:
        print(f"⚠️ PNG-Export fehlgeschlagen: {e}")


def plot_zeitslider_radioaktiv(df, ergebnisse_dir, unterordner, filename_ohne_ext):
    """
    Erstellt eine zeitsensitive Radioaktivitätskarte (Folium) und speichert HTML und PNG.
    """
    sensor = 'Radiation_CPS'

    df = df[['GPS_Lat', 'GPS_Lon', 'DateTime', sensor]].dropna()
    df = df[df[sensor] >= 0]
    df['DateTime'] = pd.to_datetime(df['DateTime'], errors='coerce')

    features = []
    for _, row in df.iterrows():
        cps = row[sensor]
        # Für CPS < 1: komplett transparent (rgba mit alpha=0)
        if cps < 1:
            color = 'rgba(0,0,0,0)'
        elif cps < 2:
            color = 'gray'
        else:
            color = 'black'

        feature = {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [row['GPS_Lon'], row['GPS_Lat']],
            },
            'properties': {
                'time': row['DateTime'].isoformat(),
                'style': {'color': color},
                'icon': 'circle',
                'iconstyle': {
                    'fillColor': color,
                    'fillOpacity': 0.9,
                    'stroke': False,
                    'radius': 6
                },
                'popup': f"Radioaktivität: {cps:.2f} CPS<br>Datum: {row['DateTime']}"
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

    # Legende
    legend_html = '''
    <div style="position: fixed; bottom: 50px; left: 50px; width: 260px; background-color: white; z-index:9999; font-size:13px; border:1px solid #bbb; border-radius:8px; padding:8px;">
        <b>Farbskala: Radioaktivität (CPS)</b><br>
        <div style="margin-top:6px;">
            <span style="display:inline-block;width:18px;height:18px;background:linear-gradient(to right,rgba(0,0,0,0),rgba(0,0,0,0));border:1px solid #bbb;"></span>
            <span style="margin-left:8px;">CPS &lt; 1 (transparent)</span>
        </div>
        <div style="margin-top:4px;">
            <span style="display:inline-block;width:18px;height:18px;background:gray;border:1px solid #bbb;"></span>
            <span style="margin-left:8px;">CPS 1–1.9 (leicht erhöht)</span>
        </div>
        <div style="margin-top:4px;">
            <span style="display:inline-block;width:18px;height:18px;background:black;border:1px solid #bbb;"></span>
            <span style="margin-left:8px;">CPS ≥ 2 (hoch)</span>
        </div>
        <div style="margin-top:6px;font-size:11px;color:#555;">Frank Albrecht</div>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))

    # Speicherpfade
    os.makedirs(unterordner, exist_ok=True)
    html_path = os.path.join(unterordner, f"{filename_ohne_ext}_radioaktiv.html")
    png_path = os.path.join(unterordner, f"{filename_ohne_ext}_radioaktiv.png")
    m.save(html_path)
    print(f"✅ HTML gespeichert: {html_path}")

    # PNG per Screenshot (am letzten Zeitschritt)
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--window-size=1600x1000')
        driver = webdriver.Chrome(options=options)
        driver.get("file://" + os.path.abspath(html_path))

        # Warten, bis Zeitslider geladen ist
        time.sleep(2)

        # ➤ JavaScript: Zeitslider ganz nach rechts setzen
        script = """
        let sliders = document.getElementsByClassName('leaflet-control-timecontrol');
        if (sliders.length) {
            let input = sliders[0].querySelector('input[type=\"range\"]');
            if (input) input.value = input.max;
            let evt = new Event('input', { bubbles: true });
            input.dispatchEvent(evt);
        }
        """
        driver.execute_script(script)

        # Kurz warten für Marker-Update
        time.sleep(1)

        # Screenshot
        driver.save_screenshot(png_path)
        driver.quit()
        print(f"✅ PNG gespeichert (letzter Zeitschritt): {png_path}")
    except Exception as e:
        print(f"⚠️ PNG-Export fehlgeschlagen: {e}")


def plot_luftkarte(df, ergebnisse_dir, unterordner, filename_ohne_ext):
    # Nur Zeilen mit gültigen GPS-Daten verwenden
    df = df[(df['GPS_Lat'].notna()) & (df['GPS_Lon'].notna())]

    map_center = [49.3477, 8.1399]  # Zentrum Neustadt
    sensor_map = folium.Map(location=map_center, zoom_start=13, control_scale=True)

    def get_color(value):
        if value < 100:
            return 'green'
        elif value < 200:
            return 'orange'
        else:
            return 'red'

    marker_cluster = MarkerCluster().add_to(sensor_map)

    for _, row in df.iterrows():
        lat, lon = row['GPS_Lat'], row['GPS_Lon']
        mq135 = row.get('MQ135', 0)
        popup_text = (
            f"<b>Datum:</b> {row['DateTime']}<br>"
            f"<b>Temperatur:</b> {row.get('Temperature_DHT_C', '?')} °C<br>"
            f"<b>Luftfeuchte:</b> {row.get('Humidity_RH', '?')} %<br>"
            f"<b>MQ135 Luftqualität:</b> {mq135} µg/m³<br>"
            f"<b>Radioaktivität:</b> {row.get('Radiation_CPS', '?')} CPS"
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

    # === Legende ===
    legend_html = '''
    <div style="position: fixed; bottom: 50px; left: 50px; width: 420px; min-height: 120px; background-color: white; z-index:9999; font-size:13px; border:1px solid #bbb; border-radius:8px; padding:8px;">
        <b>Farbskala: MQ135 Luftqualität</b><br>
        <div style="margin-top:6px;">
            <span style="display:inline-block;width:18px;height:18px;background:#00cc00;border:1px solid #bbb;"></span>
            <span style="margin-left:8px;">&lt; 400 µg/m³ (gut)</span>
        </div>
        <div style="margin-top:4px;">
            <span style="display:inline-block;width:18px;height:18px;background:orange;border:1px solid #bbb;"></span>
            <span style="margin-left:8px;">400–799 µg/m³ (mittel)</span>
        </div>
        <div style="margin-top:4px;">
            <span style="display:inline-block;width:18px;height:18px;background:#cc0000;border:1px solid #bbb;"></span>
            <span style="margin-left:8px;">≥ 800 µg/m³ (hoch)</span>
        </div>
        <hr style="margin:8px 0;">
        <b>Luftqualitäts-Klassifikation (Richtwerte)</b><br>
        <table style="border-collapse:collapse;width:100%;font-size:12px;">
            <tr style="background:#f0f0f0;"><th style="border:1px solid #bbb;padding:2px;">Luftqualität</th><th style="border:1px solid #bbb;padding:2px;">CO₂ (ppm)</th><th style="border:1px solid #bbb;padding:2px;">CO₂ (µg/m³)</th><th style="border:1px solid #bbb;padding:2px;">NH₃/NOx (µg/m³)</th></tr>
            <tr><td style="border:1px solid #bbb;padding:2px;">Frischluft</td><td style="border:1px solid #bbb;padding:2px;">400–500</td><td style="border:1px solid #bbb;padding:2px;">720–900</td><td style="border:1px solid #bbb;padding:2px;">&lt; 50</td></tr>
            <tr><td style="border:1px solid #bbb;padding:2px;">Normal</td><td style="border:1px solid #bbb;padding:2px;">500–1000</td><td style="border:1px solid #bbb;padding:2px;">900–1800</td><td style="border:1px solid #bbb;padding:2px;">50–200</td></tr>
            <tr><td style="border:1px solid #bbb;padding:2px;">Mäßig belastet</td><td style="border:1px solid #bbb;padding:2px;">1000–2000</td><td style="border:1px solid #bbb;padding:2px;">1800–3600</td><td style="border:1px solid #bbb;padding:2px;">200–500</td></tr>
            <tr><td style="border:1px solid #bbb;padding:2px;">Schlecht</td><td style="border:1px solid #bbb;padding:2px;">&gt; 2000</td><td style="border:1px solid #bbb;padding:2px;">&gt; 3600</td><td style="border:1px solid #bbb;padding:2px;">&gt; 500</td></tr>
        </table>
        <div style="margin-top:6px;font-size:11px;color:#555;">Frank Albrecht</div>
    </div>
    '''
    sensor_map.get_root().html.add_child(folium.Element(legend_html))

    # === Export ===
    os.makedirs(unterordner, exist_ok=True)
    output_file = os.path.join(unterordner, f"punktluftwert_{filename_ohne_ext}.html")
    sensor_map.save(output_file)
    print(f"✅ Karte gespeichert: {output_file}")

def plot_sensorverläufe_mit_pdf(df, ergebnisse_dir, unterordner, filename_ohne_ext):
    """
    Erstellt Liniendiagramme für viele Sensorwerte.
    Speichert PNGs und erstellt automatisch ein PDF mit allen Diagrammen.
    """
    sensor_spalten = [
        'Temperature_DHT_C', 'Humidity_RH', 'Light_Level', 'Light_Percent',
        'MQ2', 'MQ3', 'MQ4', 'MQ5', 'MQ6', 'MQ7', 'MQ8', 'MQ9', 'MQ135',
        'Mic1', 'Mic2', 'Radiation_CPS'
    ]

    os.makedirs(ergebnisse_dir, exist_ok=True)
    os.makedirs(unterordner, exist_ok=True)

    pdf_path = os.path.join(unterordner, f"{filename_ohne_ext}_sensorplots.pdf")
    with PdfPages(pdf_path) as pdf:
        for sensor in sensor_spalten:
            if sensor not in df.columns:
                print(f"⚠️ Spalte '{sensor}' nicht gefunden – übersprungen.")
                continue

            try:
                plt.figure(figsize=(10, 4))
                df[sensor].plot(title=f'{sensor} Verlauf')
                plt.ylabel(sensor)
                plt.xlabel('Index')
                plt.grid(True)

                # PNG speichern
                pfad1 = os.path.join(ergebnisse_dir, f"{sensor}_{filename_ohne_ext}.png")
                pfad2 = os.path.join(unterordner, f"{filename_ohne_ext}_{sensor}.png")
                plt.savefig(pfad1)
                plt.savefig(pfad2)

                # PDF-Seite hinzufügen
                pdf.savefig()
                plt.close()

                print(f"✅ Diagramm gespeichert: {sensor}")
            except Exception as e:
                print(f"❌ Fehler bei {sensor}: {e}")

    print(f"\n📄 PDF mit allen Diagrammen gespeichert unter:\n{pdf_path}")

def plot_sensoren_zeitverlauf(df, ergebnisse_dir, unterordner, filename_ohne_ext):
    """
    Erstellt ein Liniendiagramm für den Verlauf mehrerer Sensoren.
    - Sensorskala passt sich Datenbereich an
    - Rechts Skala für Temperatur (0-100°C) und Luftfeuchtigkeit (0-100%)
    - Radiation als vertikale Linien (in Legende gekennzeichnet)
    - Gasnamen in Legende ergänzt
    """
    plt.figure(figsize=(14, 6))
    
    # Zeitachse aus DateTime-Spalte erstellen
    zeit = pd.to_datetime(df['DateTime'])
    
    # Hauptachsen für Sensoren
    ax1 = plt.gca()
    
    # Gas-Sensoren mit ihren gemessenen Gasen
    gas_sensoren = {
        'MQ2': 'Kombi (H2,LPG,CH4,CO,Alkohol)',
        'MQ3': 'Alkohol',
        'MQ4': 'Methan/CNG',
        'MQ5': 'Kombi (LPG,Erdgas,Stadtgas)',
        'MQ6': 'LPG/Propan/Butan',
        'MQ7': 'Kohlenmonoxid (CO)',
        'MQ8': 'Wasserstoff (H2)',
        'MQ9': 'Kombi (CO,brennbare Gase)',
        'MQ135': 'Kombi (NH3,NOx,Alkohol,Benzin,CO2)'
    }
    
    # Alle Gassensoren plotten (dünn und halbtransparent)
    min_val, max_val = float('inf'), -float('inf')
    for sensor, gasname in gas_sensoren.items():
        ax1.plot(zeit, df[sensor], label=f"{sensor} ({gasname})", linewidth=1, alpha=0.5)
        min_val = min(min_val, df[sensor].min())
        max_val = max(max_val, df[sensor].max())
    
    # Temperatur und Luftfeuchtigkeit auf rechter Achse
    ax2 = ax1.twinx()
    ax2.plot(zeit, df['Temperature_DHT_C'], label='Temperatur (°C)', 
             linewidth=3, color='red')
    ax2.plot(zeit, df['Humidity_RH'], label='Luftfeuchtigkeit (%)', 
             linewidth=3, color='blue')
    ax2.set_ylim(0, 80, 5)  # Fixe Skala 0-80 für beide Werte
    ax2.set_ylabel('Temperatur (°C) / Luftfeuchtigkeit (%)')
    
    # Radiation_CPS als senkrechte Linien plotten (auf Hauptachse)
    rad_lines = []
    for t, rad in zip(zeit, df['Radiation_CPS']):
        if rad > 0:
            line = ax1.plot([t, t], [min_val, min_val + 0.1*(max_val-min_val)], 
                          color='green', linewidth=1, alpha=0.7)
            if not rad_lines:  # Nur erste Linie für Legende
                rad_lines = line
    
    # Achsen anpassen
    ax1.set_xlabel('Zeit')
    ax1.set_ylabel('Gassensorwerte (ppm/relative Werte)')
    ax1.set_title('Sensorverlauf über die Zeit')
    ax1.grid(True)
    
    # Formatierung der Zeitachse
    plt.gcf().autofmt_xdate()
    
    # Kombinierte Legende
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    if rad_lines:
        lines1.extend(rad_lines)
        labels1.append('Radiation (CPS)')
    
    ax1.legend(lines1 + lines2, labels1 + labels2, 
              bbox_to_anchor=(1.25, 1), loc='upper left')
    
    plt.tight_layout()
    
    # Speichern der Grafik
    pfad1a = os.path.join(ergebnisse_dir, f"sensorverlauf_{filename_ohne_ext}.png")
    pfad1b = os.path.join(unterordner, f"{filename_ohne_ext}_sensorverlauf.png")
    plt.savefig(pfad1a, dpi=300, bbox_inches='tight')
    plt.savefig(pfad1b, dpi=300, bbox_inches='tight')
    plt.close()



def plot_3d(df, ergebnisse_dir, unterordner, filename_ohne_ext):
    """
    Erstellt einen realitätsnah skalierten 3D-Plot (Longitude, Latitude → Meter) mit Höhe und Temperatur.
    Speichert als HTML-Datei.
    """
    # Spaltennamen trimmen
    df.columns = df.columns.str.strip()

    # Spalten erkennen
    x_col = 'GPS_Lon' if 'GPS_Lon' in df.columns else 'lon'
    y_col = 'GPS_Lat' if 'GPS_Lat' in df.columns else 'lat'
    z_col = 'GPS_Alt' if 'GPS_Alt' in df.columns else ('Höhe' if 'Höhe' in df.columns else ('hoehe' if 'hoehe' in df.columns else 'z'))
    color_col = 'Temperature_DHT_C' if 'Temperature_DHT_C' in df.columns else ('temperatur' if 'temperatur' in df.columns else None)

    if not all(col in df.columns for col in [x_col, y_col, z_col]) or color_col is None:
        print("⚠️ 3D-Plot: Benötigte Spalten nicht gefunden. Überspringe plot_3d.")
        return

    # Mittelwert der Längengrade → UTM-Zone berechnen
    mean_lon = df[x_col].mean()
    utm_zone = int((mean_lon + 180) / 6) + 1
    utm_crs = f"EPSG:{32600 + utm_zone}"  # Nur Nordhalbkugel – für Südhalbkugel ggf. anpassen

    # Transformation vorbereiten
    transformer = Transformer.from_crs("EPSG:4326", utm_crs, always_xy=True)
    df['x_m'], df['y_m'] = transformer.transform(df[x_col].values, df[y_col].values)

    # Plotly 3D-Scatterplot mit dunkelgrüner Bodenfläche
    scatter = go.Scatter3d(
        x=df['x_m'],
        y=df['y_m'],
        z=df[z_col],
        mode='markers',
        marker=dict(
            size=4,
            color=df[color_col],
            colorscale='RdBu_r',  # Rot = warm, Blau = kalt
            cmin=0,
            cmax=40,
            opacity=0.8,
            colorbar=dict(title=f"{color_col} (°C)", tickvals=[0,10,20,30,40], ticktext=["0°C (kalt)","10°C","20°C","30°C","40°C (heiß)"])
        ),
        name='Messpunkte'
    )

    # Bodenfläche berechnen (rechteckig über Bereich der Messpunkte)
    x_min, x_max = df['x_m'].min(), df['x_m'].max()
    y_min, y_max = df['y_m'].min(), df['y_m'].max()
    z_floor = df[z_col].min()
    # Gitter für Bodenfläche
    x_floor = [x_min, x_max]
    y_floor = [y_min, y_max]
    X, Y = np.meshgrid(x_floor, y_floor)
    Z = np.full_like(X, z_floor)

    surface = go.Surface(
        x=X,
        y=Y,
        z=Z,
        showscale=False,
        opacity=0.7,
        colorscale=[[0, 'darkgreen'], [1, 'darkgreen']],
        name='Boden (dunkelgrün)'
    )

    fig = go.Figure(data=[surface, scatter])

    # Layout mit realistischer Skalierung
    fig.update_layout(
        scene=dict(
            xaxis_title="Easting (m)",
            yaxis_title="Northing (m)",
            zaxis_title=z_col,
            aspectmode='data'  # Skaliert alles proportional zu realen Datenbereichen
        ),
        legend=dict(x=0.8, y=0.9)
    )

    # HTML speichern
    os.makedirs(unterordner, exist_ok=True)
    out_path = os.path.join(unterordner, f"{filename_ohne_ext}_3dplot.html")
    fig.write_html(out_path)
    print(f"✅ 3D-Plot gespeichert: {out_path}")

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
        plot_luftkarte,
        plot_sensorverläufe_mit_pdf,
        plot_zeitslider_radioaktiv,
        plot_zeitslider_lautstaerke,
        plot_3d,
        plot_sensoren_zeitverlauf,
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
    return True


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
