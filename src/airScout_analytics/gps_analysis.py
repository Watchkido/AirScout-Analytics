from csv_analyser.config import CONFIG

def pruefe_und_analysiere_gps(df):
    """
    Prüft, ob GPS-Spalten im DataFrame vorhanden sind und gibt ggf. die GPS-Auswertung als Liste von Strings zurück.
    Gibt None zurück, falls keine GPS-Spalten gefunden werden.
    """
    gps_lat_names = ("lat", "latitude", "gps_lat", "gps_latitude")
    gps_lon_names = ("lon", "lng", "longitude", "gps_lon", "gps_lng", "gps_longitude")
    lat_cols = [c for c in df.columns if c.lower().replace(" ", "").replace("-", "_") in gps_lat_names]
    lon_cols = [c for c in df.columns if c.lower().replace(" ", "").replace("-", "_") in gps_lon_names]
    if lat_cols and lon_cols:
        return gps_auswertung(df)
    return None
"""
Modul für GPS-Auswertungen (Strecke, Geschwindigkeit, Heatmap etc.)
Autor: Frank Albrecht
Datum: 2025-07-21
"""


import pandas as pd
from typing import List
def gps_auswertung(df: pd.DataFrame) -> List[str]:
    """
    Führt eine spezielle GPS-Auswertung durch: Streckenberechnung, Geschwindigkeit, Heatmap.
    :param df: DataFrame mit GPS-Daten (Spalten: lat, lon, ggf. Zeit)
    :returns: Liste von Analyse-Strings
    """
    ergebnisse = []
    lat_col = None
    lon_col = None
    zeit_col = None

    def normiere(name):
        return name.strip().lower().replace(" ", "_").replace("-", "_")

    lat_aliases = {"lat", "latitude", "gps_lat", "gps_latitude", "gpslat", "gpslatitude"}
    lon_aliases = {"lon", "lng", "longitude", "gps_lon", "gps_lng", "gps_longitude", "gpslon", "gpslongitude"}
    zeit_aliases = {"zeit", "time", "timestamp", "datetime", "gps_datetime", "gps_time", "gpstimestamp", "gpsdatetime"}

    for col in df.columns:
        n = normiere(col)
        if n in lat_aliases:
            lat_col = col
        if n in lon_aliases:
            lon_col = col
        if n in zeit_aliases:
            zeit_col = col

    if not lat_col or not lon_col:
        ergebnisse.append("❌ Keine GPS-Koordinaten gefunden (lat/lon)")
        return ergebnisse

    from math import radians, sin, cos, sqrt, atan2
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371.0
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return R * c

    lat = pd.to_numeric(df[lat_col], errors='coerce').values
    lon = pd.to_numeric(df[lon_col], errors='coerce').values
    strecke_km = 0.0
    for i in range(1, len(lat)):
        if not (pd.isna(lat[i-1]) or pd.isna(lon[i-1]) or pd.isna(lat[i]) or pd.isna(lon[i])):
            strecke_km += haversine(lat[i-1], lon[i-1], lat[i], lon[i])
    ergebnisse.append(f"🗺️ Gesamte Strecke: {strecke_km:.3f} km")

    if zeit_col:
        try:
            zeit = pd.to_datetime(df[zeit_col], errors='coerce')
            zeiten_s = (zeit - zeit.iloc[0]).dt.total_seconds().values
            gesamtzeit_h = (zeiten_s[-1] - zeiten_s[0]) / 3600 if len(zeiten_s) > 1 else 0
            if gesamtzeit_h > 0:
                v_avg = strecke_km / gesamtzeit_h
                ergebnisse.append(f"🚗 Durchschnittsgeschwindigkeit: {v_avg:.2f} km/h")
            else:
                ergebnisse.append("⚠️ Zeitspanne zu kurz oder nur ein Zeitwert")
        except Exception as e:
            ergebnisse.append(f"⚠️ Zeitspalte konnte nicht ausgewertet werden: {e}")
    else:
        ergebnisse.append("ℹ️ Keine Zeitspalte für Geschwindigkeitsberechnung gefunden")

    ergebnisse.append("🌡️ Heatmap der GPS-Punkte kann mit externer Visualisierung erzeugt werden (z.B. mit folium oder matplotlib)")
    return ergebnisse


# Test-Block für direkten Modulstart
if __name__ == "__main__":
    import pandas as pd
    print("[Demo] Starte Beispiel-GPS-Auswertung...")
    # Beispiel-DataFrame mit GPS- und Zeitdaten
    df_demo = pd.DataFrame({
        'lat': [52.5, 52.6, 52.7],
        'lon': [13.4, 13.5, 13.6],
        'zeit': ["2025-07-24 10:00:00", "2025-07-24 10:10:00", "2025-07-24 10:30:00"]
    })
    result = pruefe_und_analysiere_gps(df_demo)
    print("--- Ergebnis ---")
    for line in result:
        print(line)
