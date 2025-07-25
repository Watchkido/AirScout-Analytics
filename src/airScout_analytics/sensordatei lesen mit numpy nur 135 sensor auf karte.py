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
plt.figure(figsize=(14, 7))
for sensor in gassensoren:
    if sensor in df.columns:
        plt.plot(df["DateTime"], df[sensor], label=sensor)

plt.title("Gassensoren über Zeit")
plt.xlabel("Zeit")
plt.ylabel("Sensor-Rohwerte")
plt.legend()
plt.grid(True)
plt.tight_layout()
verlauf_datei = os.path.expanduser(f"~/Downloads/{dateiname.replace('.csv', '')}_verlauf.png")
plt.savefig(verlauf_datei)
plt.close()
print("Sensorverlauf gespeichert als 'gassensoren_verlauf.png'.")


# === 6. CO-Alarm (MQ7 > 300) ===
co_limit = 300
if "MQ7" in df.columns:
    co_alarme = df[df["MQ7"] > co_limit]
    print(f"Anzahl CO-Alarme (MQ7 > {co_limit}): {len(co_alarme)}")
    if not co_alarme.empty:
        print(co_alarme[["DateTime", "MQ7"]].head())

        # Plot CO-Alarme
        plt.figure(figsize=(12, 6))
        plt.plot(co_alarme["DateTime"], co_alarme["MQ7"], marker="o", linestyle="-")
        plt.title(f"CO-Alarme (MQ7 > {co_limit})")
        plt.xlabel("Zeit")
        plt.ylabel("MQ7-Wert")
        plt.grid(True)
        plt.tight_layout()
        coalarme_datei = os.path.expanduser(f"~/Downloads/{dateiname.replace('.csv', '')}_coalarme.png")
        plt.savefig(coalarme_datei)
        plt.close()
        print(f"CO-Alarm-Verlauf gespeichert als '{coalarme_datei}'.")

# === 7. MQ135 glätten und plotten ===
def gleitender_mittelwert(array, fenster=10):
    return np.convolve(array, np.ones(fenster)/fenster, mode='valid')

if "MQ135" in df.columns:

    mq135_array = df["MQ135"].to_numpy()
    mq135_glatt = gleitender_mittelwert(mq135_array, fenster=10)

    # Plot
    plt.plot(df["DateTime"][5:-4], mq135_glatt)
    plt.title("MQ135 (geglättet)")
    plt.xlabel("Zeit")
    plt.ylabel("Sensorwert")
    plt.grid(True)
    plt.tight_layout()
    mq135_datei = os.path.expanduser(f"~/Downloads/{dateiname.replace('.csv', '')}_geglättet.png")
    plt.savefig(mq135_datei)
    plt.close()
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

    # Orte mit höchsten MQ135-Werten (oberes Dezil) auf Karte darstellen
    try:
        import folium
        # Filter: gültige GPS und MQ135 Werte obere 10 prozent 0.9 quantil
        df_valid = df[df["MQ135"].notna() & df["GPS_Lat"].notna() & df["GPS_Lon"].notna()]
        if not df_valid.empty:

            mq135_threshold = df_valid["MQ135"].quantile(0.9)
            top10_luft = df_valid[df_valid["MQ135"] >= mq135_threshold]
            if not top10_luft.empty:
                lat_mittel = top10_luft["GPS_Lat"].mean()
                lon_mittel = top10_luft["GPS_Lon"].mean()
                m = folium.Map(location=[lat_mittel, lon_mittel], zoom_start=12)
                for _, row in top10_luft.iterrows():
                    folium.Marker(
                        location=[row["GPS_Lat"], row["GPS_Lon"]],
                        popup=f"{row['DateTime']} MQ135={row['MQ135']}",
                        icon=folium.Icon(color='red')
                    ).add_to(m)
                map_datei = os.path.expanduser(f"~/Downloads/{dateiname.replace('.csv', '')}_schlechte_luft.html")
                m.save(map_datei)
                print(f"Karte mit den 10% höchsten MQ135-Werten gespeichert als '{map_datei}'.")
            else:
                print("Keine Orte mit hohen MQ135-Werten gefunden.")
        else:
            print("Keine gültigen GPS/MQ135-Daten gefunden.")
    except ImportError:
        print("Das Paket 'folium' ist nicht installiert. Bitte mit 'pip install folium' nachinstallieren.")

# === 8. Korrelationen anzeigen ===
korrelationen = df[gassensoren].corr()
print("\nKorrelationsmatrix der Gassensoren:")
print(korrelationen.round(2))



print("\nAnalyse abgeschlossen.")
