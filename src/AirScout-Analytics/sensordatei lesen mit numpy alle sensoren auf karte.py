import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# === 1. Pfad zur Datei === und Auswahl anbieten ===
import glob
datenordner = os.path.expanduser("E:/dev/projekt_python_venv/airscout-analytics/data/roh/")
csv_dateien = glob.glob(os.path.join(datenordner, "*.csv"))
csv_dateien = [os.path.basename(f) for f in csv_dateien]

if not csv_dateien:
    print("Keine CSV-Dateien im Datenordner gefunden.")
    exit()

print("Wähle eine Datei aus:")
for i, fname in enumerate(csv_dateien, 1):
    print(f"{i}: {fname}")

wahl = input(f"Bitte Nummer eingeben (1-{len(csv_dateien)}): ")
try:
    idx = int(wahl) - 1
    if idx < 0 or idx >= len(csv_dateien):
        raise ValueError
    dateiname = csv_dateien[idx]
except Exception:
    print("Ungültige Eingabe. Abbruch.")
    exit()

pfad = os.path.join(datenordner, dateiname)

# === 2. CSV-Datei laden ===
try:
    df = pd.read_csv(pfad, comment="#")
    print("Datei erfolgreich geladen.")
except FileNotFoundError:
    print("Datei nicht gefunden. Bitte stelle sicher, dass sie im Download-Ordner liegt.")
    exit()


# GPS-Spalten in float konvertieren
for gps_col in ["GPS_Lat", "GPS_Lon"]:
    if gps_col in df.columns:
        df[gps_col] = pd.to_numeric(df[gps_col], errors="coerce")

# Zeilen mit fehlenden Werten entfernen
df = df.dropna()

# Die ersten 10 Minuten (600 Sekunden) jedes Datensatzes entfernen
if "SecSinceMidnight-MS" in df.columns:
    # Extrahiere Sekunden (vor dem Bindestrich, als Zahl)
    df["_sec"] = df["SecSinceMidnight-MS"].astype(str).str.split("-").str[0].astype(float)
    df = df[df["_sec"] > 600]
    df = df.drop(columns=["_sec"])


# === 3. Zeitstempel in datetime umwandeln ===
# Suche nach einer Spalte, die mit 'DateTime' beginnt
datetime_spalte = None
for col in df.columns:
    if col.startswith("DateTime"):
        datetime_spalte = col
        break
if not datetime_spalte:
    # Fallback: Suche nach Spalten, die 'DateTime' enthalten
    for col in df.columns:
        if "DateTime" in col:
            datetime_spalte = col
            break
if not datetime_spalte:
    print("Keine DateTime-Spalte gefunden! Verfügbare Spalten:", list(df.columns))
    exit()

# Zeitstempelspalte in datetime umwandeln
df["DateTime"] = pd.to_datetime(df[datetime_spalte].str.replace(r" MESZ| UTC", "", regex=True), errors="coerce")

# === 4. Gassensoren definieren ===
gassensoren = ["MQ2", "MQ3", "MQ4", "MQ5", "MQ6", "MQ7", "MQ8", "MQ9", "MQ135"]

# === 5. Plot: Gassensorverlauf ===

# Zeitachse bestimmen (für alle Umweltplots)
zeitachsen = [col for col in ["DateTime", "GPS_DateTime"] if col in df.columns]
if zeitachsen:
    zeit_col = zeitachsen[0]
else:
    zeit_col = None

# Zusatzdiagramm: Temperatur, Feuchte, Radioaktivität gemeinsam
# Nutze die gleiche Zeitachse wie oben (zeit_col)
if zeit_col:
    fig, ax1 = plt.subplots(figsize=(14, 7))
    plotted = False
    # Temperatur
    temp_spalten = [col for col in ["Temperatur", "Temp"] if col in df.columns]
    for tcol in temp_spalten:
        daten = df[[zeit_col, tcol]].dropna()
        daten = daten[daten[tcol] > 0]
        daten_log = daten[daten[tcol] > 50].copy()
        if not daten_log.empty:
            ax1.plot(daten_log[zeit_col], np.log10(daten_log[tcol]), label=f"log10({tcol})", color="crimson", linestyle="--", linewidth=2)
            plotted = True
    ax1.set_ylabel("log10(Temperatur [°C])", color="crimson")
    ax1.tick_params(axis='y', labelcolor="crimson")

    # Feuchtigkeit auf zweiter Achse
    feucht_spalten = [col for col in ["Hygrometer", "Feuchtigkeit"] if col in df.columns]
    if feucht_spalten:
        ax2 = ax1.twinx()
        for fcol in feucht_spalten:
            daten = df[[zeit_col, fcol]].dropna()
            daten = daten[daten[fcol] > 0]
            daten_log = daten[daten[fcol] > 50].copy()
            if not daten_log.empty:
                ax2.plot(daten_log[zeit_col], np.log10(daten_log[fcol]), label=f"log10({fcol})", color="deepskyblue", linestyle=":", linewidth=2)
                plotted = True
        ax2.set_ylabel("log10(Feuchte [%])", color="deepskyblue")
        ax2.tick_params(axis='y', labelcolor="deepskyblue")
    else:
        ax2 = None

    # Radioaktivität auf dritter Achse
    radio_spalten = [col for col in ["Radioaktivität", "Radioaktivitaet"] if col in df.columns]
    if radio_spalten:
        ax3 = ax1.twinx()
        ax3.spines["right"].set_position((1.12, 0))
        for rcol in radio_spalten:
            daten = df[[zeit_col, rcol]].dropna()
            daten = daten[daten[rcol] > 0]
            daten_log = daten[daten[rcol] > 50].copy()
            if not daten_log.empty:
                ax3.plot(daten_log[zeit_col], np.log10(daten_log[rcol]), label=f"log10({rcol})", color="black", linestyle="-.", linewidth=2)
                plotted = True
        ax3.set_ylabel("log10(Radioaktivität [Imp/min])", color="black")
        ax3.tick_params(axis='y', labelcolor="black")
    else:
        ax3 = None

    if plotted:
        fig.suptitle("Umweltwerte (log10, nur Werte > 50): Temperatur, Feuchte, Radioaktivität über Zeit")
        fig.tight_layout(rect=(0, 0, 1, 0.97))
        # Legenden aller Achsen kombinieren
        handles, labels = ax1.get_legend_handles_labels()
        if ax2:
            h2, l2 = ax2.get_legend_handles_labels()
            handles += h2
            labels += l2
        if ax3:
            h3, l3 = ax3.get_legend_handles_labels()
            handles += h3
            labels += l3
        fig.legend(handles, labels, loc="upper center", ncol=3)
        umwelt_datei = os.path.expanduser(f"~/Downloads/umweltwerte_{dateiname.replace('.csv', '')}.png")
        plt.savefig(umwelt_datei)
        plt.close(fig)
        print(f"Umweltwerte-Diagramm (log10, >50) gespeichert als '{umwelt_datei}'.")
    else:
        print("Warnung: Keine Werte > 50 für Temperatur, Feuchte oder Radioaktivität zum log-Plotten vorhanden.")
else:
    print("Keine geeignete Zeitspalte (DateTime oder GPS_DateTime) für das Umweltwerte-Diagramm gefunden.")

# --- Sensor-Rohwerte mit Temperatur und Feuchtigkeit im selben Plot ---
fig, ax1 = plt.subplots(figsize=(14, 7))
# Gassensoren auf Achse 1
for sensor in gassensoren:
    if sensor in df.columns:
        ax1.plot(df["DateTime"], df[sensor], label=sensor)
# Temperatur direkt auf Achse 1 (gestrichelt, rot)
temp_spalten = [col for col in ["Temperatur", "Temp"] if col in df.columns]
for tcol in temp_spalten:
    ax1.plot(df["DateTime"], df[tcol], label=f"{tcol}", color="crimson", linestyle="--", linewidth=2)
# Feuchtigkeit direkt auf Achse 1 (gepunktet, blau)
feucht_spalten = [col for col in ["Hygrometer", "Feuchtigkeit"] if col in df.columns]
for fcol in feucht_spalten:
    ax1.plot(df["DateTime"], df[fcol], label=f"{fcol}", color="deepskyblue", linestyle=":", linewidth=2)
ax1.set_ylabel("Sensor-Rohwerte / Temperatur [°C] / Feuchte [%]")
ax1.set_xlabel("Zeit")
ax1.grid(True)
fig.suptitle("Gassensoren, Temperatur und Feuchtigkeit über Zeit")
fig.tight_layout(rect=(0, 0, 1, 0.97))
handles, labels = ax1.get_legend_handles_labels()
fig.legend(handles, labels, loc="upper center", ncol=4)
verlauf_datei = os.path.expanduser(f"~/Downloads/verlauf_{dateiname.replace('.csv', '')}.png")
plt.savefig(verlauf_datei)
plt.close(fig)
print("Sensorverlauf gespeichert als 'gassensoren_verlauf.png'.")


# === 6. CO-Alarm (MQ7 > 300) ===
co_limit = 300
if "MQ7" in df.columns:
    co_alarme = df[df["MQ7"] > co_limit]
    print(f"Anzahl CO-Alarme (MQ7 > {co_limit}): {len(co_alarme)}")
    if not co_alarme.empty:
        print(co_alarme[["DateTime", "MQ7"]].head())

        # Plot CO-Alarme
        fig, ax1 = plt.subplots(figsize=(12, 6))
        ax1.plot(co_alarme["DateTime"], co_alarme["MQ7"], marker="o", linestyle="-", label="MQ7")
        ax1.set_ylabel("MQ7")
        ax1.set_xlabel("Zeit")
        ax1.grid(True)
        # Temperatur
        if temp_spalten:
            ax2 = ax1.twinx()
            for tcol in temp_spalten:
                if tcol in co_alarme.columns:
                    ax2.plot(co_alarme["DateTime"], co_alarme[tcol], label=tcol, color="crimson", linestyle="--")
            ax2.set_ylabel("Temperatur [°C]", color="crimson")
            ax2.tick_params(axis='y', labelcolor="crimson")
        else:
            ax2 = None
        # Feuchtigkeit
        if feucht_spalten:
            ax3 = ax1.twinx()
            ax3.spines["right"].set_position((1.12, 0))
            for fcol in feucht_spalten:
                if fcol in co_alarme.columns:
                    ax3.plot(co_alarme["DateTime"], co_alarme[fcol], label=fcol, color="deepskyblue", linestyle=":")
            ax3.set_ylabel("Feuchte [%]", color="deepskyblue")
            ax3.tick_params(axis='y', labelcolor="deepskyblue")
        else:
            ax3 = None
        # Radioaktivität
        radio_spalten = [col for col in ["Radioaktivität", "Radioaktivitaet"] if col in co_alarme.columns]
        if radio_spalten:
            ax4 = ax1.twinx()
            ax4.spines["right"].set_position((1.24, 0))
            for rcol in radio_spalten:
                if rcol in co_alarme.columns:
                    ax4.plot(co_alarme["DateTime"], co_alarme[rcol], label=rcol, color="black", linestyle="-.")
            ax4.set_ylabel("Radioaktivität [Imp/min]", color="black")
            ax4.tick_params(axis='y', labelcolor="black")
        else:
            ax4 = None
        fig.suptitle(f"CO-Alarme (MQ7 > {co_limit})")
        fig.tight_layout(rect=(0, 0, 1, 0.97))
        handles, labels = ax1.get_legend_handles_labels()
        if ax2:
            h2, l2 = ax2.get_legend_handles_labels()
            handles += h2
            labels += l2
        if ax3:
            h3, l3 = ax3.get_legend_handles_labels()
            handles += h3
            labels += l3
        if ax4:
            h4, l4 = ax4.get_legend_handles_labels()
            handles += h4
            labels += l4
        fig.legend(handles, labels, loc="upper center", ncol=4)
        coalarme_datei = os.path.expanduser(f"~/Downloads/coalarme_{dateiname.replace('.csv', '')}.png")
        plt.savefig(coalarme_datei)
        plt.close(fig)
        print(f"CO-Alarm-Verlauf gespeichert als '{coalarme_datei}'.")

# === 7. MQ135 glätten und plotten ===
def gleitender_mittelwert(array, fenster=10):
    return np.convolve(array, np.ones(fenster)/fenster, mode='valid')

if "MQ135" in df.columns:

    mq135_array = df["MQ135"].to_numpy()
    mq135_glatt = gleitender_mittelwert(mq135_array, fenster=10)

    # Plot
    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax1.plot(df["DateTime"][5:-4], mq135_glatt, label="MQ135 (geglättet)")
    ax1.set_ylabel("MQ135 (geglättet)")
    ax1.set_xlabel("Zeit")
    ax1.grid(True)
    # Temperatur
    if temp_spalten:
        ax2 = ax1.twinx()
        for tcol in temp_spalten:
            ax2.plot(df["DateTime"], df[tcol], label=tcol, color="crimson", linestyle="--")
        ax2.set_ylabel("Temperatur [°C]", color="crimson")
        ax2.tick_params(axis='y', labelcolor="crimson")
    else:
        ax2 = None
    # Feuchtigkeit
    if feucht_spalten:
        ax3 = ax1.twinx()
        ax3.spines["right"].set_position((1.12, 0))
        for fcol in feucht_spalten:
            ax3.plot(df["DateTime"], df[fcol], label=fcol, color="deepskyblue", linestyle=":")
        ax3.set_ylabel("Feuchte [%]", color="deepskyblue")
        ax3.tick_params(axis='y', labelcolor="deepskyblue")
    else:
        ax3 = None
    # Radioaktivität
    if radio_spalten:
        ax4 = ax1.twinx()
        ax4.spines["right"].set_position((1.24, 0))
        for rcol in radio_spalten:
            ax4.plot(df["DateTime"], df[rcol], label=rcol, color="black", linestyle="-.")
        ax4.set_ylabel("Radioaktivität [Imp/min]", color="black")
        ax4.tick_params(axis='y', labelcolor="black")
    else:
        ax4 = None
    fig.suptitle("MQ135 (geglättet) und Umweltwerte")
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    handles, labels = ax1.get_legend_handles_labels()
    if ax2:
        h2, l2 = ax2.get_legend_handles_labels()
        handles += h2
        labels += l2
    if ax3:
        h3, l3 = ax3.get_legend_handles_labels()
        handles += h3
        labels += l3
    if ax4:
        h4, l4 = ax4.get_legend_handles_labels()
        handles += h4
        labels += l4
    fig.legend(handles, labels, loc="upper center", ncol=4)
    mq135_datei = os.path.expanduser(f"~/Downloads/geglättet_{dateiname.replace('.csv', '')}.png")
    plt.savefig(mq135_datei)
    plt.close(fig)
    print("MQ135-Glättung gespeichert als 'mq135_geglättet.png'.")

    # Luftqualitätsbewertung
    def luftqualitaet_index(wert):
        if wert < 150:
            return "Gut"
        elif wert < 250:
            return "Mäßig"
        else:
            return "Schlecht"


    df["Luftqualitaet"] = df["MQ135"].apply(luftqualitaet_index)
    print("Letzte 5 Bewertungen der Luftqualität:")
    print(df[["DateTime", "MQ135", "Luftqualitaet"]].tail())

    # Karte: Für jeden Sensor die obersten 10% anzeigen, jeweils mit anderer Farbe und Legende
    try:
        import folium
        sensor_colors = {
            "MQ2": "red",      # LPG, Butan, Propan, Methan, H2, Alkohol, Rauch
            "MQ3": "orange",   # Alkohol, Ethanol
            "MQ4": "green",    # Methan, Erdgas
            "MQ5": "blue",     # Erdgas, LPG
            "MQ6": "purple",   # Flüssiggas
            "MQ7": "darkred",  # Kohlenmonoxid CO
            "MQ8": "darkblue", # Wasserstoff H2
            "MQ9": "cadetblue",# CO, entflammbare Gase
            "MQ135": "black"   # Luftqualität, CO2, NH3, NOx
        }
        sensor_gas = {
            "MQ2": "LPG, Butan, Propan, Methan, H2, Alkohol, Rauch",
            "MQ3": "Alkohol, Ethanol",
            "MQ4": "Methan, Erdgas",
            "MQ5": "Erdgas, LPG",
            "MQ6": "Flüssiggas",
            "MQ7": "Kohlenmonoxid (CO)",
            "MQ8": "Wasserstoff (H2)",
            "MQ9": "CO, entflammbare Gase",
            "MQ135": "Luftqualität (CO2, NH3, NOx)"
        }
        # Mittelpunkt berechnen (alle GPS)
        df_gps = df[df["GPS_Lat"].notna() & df["GPS_Lon"].notna()]
        if not df_gps.empty:
            lat_mittel = df_gps["GPS_Lat"].mean()
            lon_mittel = df_gps["GPS_Lon"].mean()
            m = folium.Map(location=[lat_mittel, lon_mittel], zoom_start=12)
            # Marker für jeden Sensor
            for sensor, farbe in sensor_colors.items():
                if sensor in df.columns:
                    df_valid = df[df[sensor].notna() & df["GPS_Lat"].notna() & df["GPS_Lon"].notna()]
                    if not df_valid.empty:
                        threshold = df_valid[sensor].quantile(0.9)
                        top10 = df_valid[df_valid[sensor] >= threshold]
                        for _, row in top10.iterrows():
                            popup_text = f"Sensor: {sensor}<br>Gas: {sensor_gas[sensor]}<br>Wert: {row[sensor]}<br>Datum/Zeit: {row['DateTime']}"
                            folium.Marker(
                                location=[row["GPS_Lat"], row["GPS_Lon"]],
                                popup=popup_text,
                                icon=folium.Icon(color=farbe)
                            ).add_to(m)
            # Alle Punkte mit Radioaktivität > 0 (egal welcher Sensor)
            radio_cols = [col for col in ["Radioaktivität", "Radioaktivitaet"] if col in df.columns]
            if radio_cols:
                for radio_col in radio_cols:
                    df_radio = df[(df[radio_col].notna()) & (df[radio_col] > 0) & df["GPS_Lat"].notna() & df["GPS_Lon"].notna()]
                    for _, row in df_radio.iterrows():
                        popup_text = f"Radioaktivität: {row[radio_col]}<br>Datum/Zeit: {row['DateTime']}"
                        folium.Marker(
                            location=[row["GPS_Lat"], row["GPS_Lon"]],
                            popup=popup_text,
                            icon=folium.Icon(color="lightgray", icon="radiation", prefix="fa")
                        ).add_to(m)
            # Legende als HTML
            legend_html = '<div style="position: fixed; bottom: 50px; left: 50px; width: 450px; height: 260px; z-index:9999; font-size:14px; background: white; border:2px solid grey; padding: 10px;">'
            legend_html += '<b>Legende: Sensorfarben und Gase</b><br>'
            for sensor, farbe in sensor_colors.items():


            legend_html += f'<i style="background:{farbe};color:{farbe};border-radius:50%;padding:4px 8px;margin-right:8px;">●</i> <b>{sensor}</b>: {sensor_gas[sensor]}<br>'
            legend_html += '</div>'
            m.get_root().html.add_child(folium.Element(legend_html))
            map_datei = os.path.expanduser(f"~/Downloads/sensor_top10_map_{dateiname.replace('.csv', '')}.html")
            m.save(map_datei)
            print(f"Karte mit den 10% höchsten Werten aller Sensoren gespeichert als '{map_datei}'.")
        else:
            print("Keine gültigen GPS-Daten gefunden.")
    except ImportError:
        print("Das Paket 'folium' ist nicht installiert. Bitte mit 'pip install folium' nachinstallieren.")

# === 8. Korrelationen anzeigen ===

# Korrelationsmatrix als Grafik speichern
import seaborn as sns

# Zusätzliche Spalten für die Korrelationsmatrix
zusatzsensoren = [
    "Temperatur", "Temp", "Hygrometer", "Feuchtigkeit", "Radioaktivität", "Radioaktivitaet", "Licht", "Light"
]
# Füge alle Spalten hinzu, die im DataFrame existieren
korrelations_spalten = [s for s in gassensoren if s in df.columns]
for zusatz in zusatzsensoren:
    if zusatz in df.columns and zusatz not in korrelations_spalten:
        korrelations_spalten.append(zusatz)

korrelationen = df[korrelations_spalten].corr()

plt.figure(figsize=(10, 8))
ax = sns.heatmap(korrelationen, annot=True, cmap="coolwarm", fmt=".2f")
plt.title("Korrelationsmatrix der Gassensoren")
# Legende als Text unterhalb des Plots
legende = "\n".join([f"{s}: {sensor_gas[s]}" for s in gassensoren if s in df.columns])
# Legende linksbündig, etwas höher, Überschrift fett und größer
plt.gcf().text(0.01, -0.01, "Gase je Sensor:", ha='left', va='top', fontsize=15, fontweight='bold')
plt.gcf().text(0.01, -0.06, legende, ha='left', va='top', fontsize=12)
plt.tight_layout(rect=(0,0.08,1,1))
korrelationsgrafik_datei = os.path.expanduser(f"~/Downloads/korrelationsmatrix_{dateiname.replace('.csv', '')}.png")
plt.savefig(korrelationsgrafik_datei, bbox_inches='tight')
plt.close()
print(f"Korrelationsgrafik gespeichert als '{korrelationsgrafik_datei}'.")

print("\nAnalyse abgeschlossen.")
