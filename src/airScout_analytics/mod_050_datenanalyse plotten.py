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
from selenium import webdriver
from PIL import Image
from folium.plugins import TimestampedGeoJson
from folium.plugins import MarkerCluster
from matplotlib.backends.backend_pdf import PdfPages
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

    # Legende
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

    # Speicherpfade
    os.makedirs(unterordner, exist_ok=True)
    html_path = os.path.join(unterordner, f"{filename_ohne_ext}_lautstaerke.html")
    png_path = os.path.join(unterordner, f"{filename_ohne_ext}_lautstaerke.png")
    m.save(html_path)
    print(f"✅ HTML gespeichert: {html_path}")

    # PNG per Screenshot (am letzten Zeitschritt)
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--window-size=1600x1000')
        driver = webdriver.Chrome(options=options)
        driver.get("file://" + os.path.abspath(html_path))

        time.sleep(2)

        # Slider ans Ende setzen
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
    <div style="position: fixed; bottom: 50px; left: 50px; width: 440px; min-height: 120px; background-color: white; z-index:9999; font-size:13px; border:1px solid #bbb; border-radius:8px; padding:8px;">
        <b>Farbskala: {sensor}</b><br>
        <span style="float:left">{min_val:.2f}</span>
        <span style="float:right">{max_val:.2f}</span>
        <div style="clear:both;"></div>
        <div style="height: 16px; background: linear-gradient(to right, #00ff00 0%, #ffff00 50%, #ff0000 100%); border:1px solid #bbb;"></div>
        <div style="margin-top:8px;"></div>
        <b>Farbskala: MQ135 Luftqualität</b><br>
        <div style="margin-top:6px;">
            <span style="display:inline-block;width:18px;height:18px;background:#00cc00;border:1px solid #bbb;"></span>
            <span style="margin-left:8px;">&lt; 400 µg/m³ (gut)</span>
        </div>
        <div style="margin-top:4px;">
            <span style="display:inline-block;width:18px;height:18px;background:orange;border:1px solid #bbb;"></span>
            <span style="margin-left:8px;">500–1000 µg/m³ (mittel)</span>
        </div>
        <div style="margin-top:4px;">
            <span style="display:inline-block;width:18px;height:18px;background:#cc0000;border:1px solid #bbb;"></span>
            <span style="margin-left:8px;">≥ 2000 µg/m³ (hoch)</span>
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
        <div style="margin-top:6px;font-size:11px;color:#555;">Hinweis: Die MQ135-Skala in dieser Karte ("mittel" ab 4000 µg/m³) entspricht bereits einer extrem belasteten Luft nach offiziellen Richtwerten.</div>
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
        plot_zeitslider,
        plot_luftkarte,
        plot_sensorverläufe_mit_pdf,
        plot_zeitslider_radioaktiv,
        plot_zeitslider_lautstaerke,
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
