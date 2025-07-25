from geopy.geocoders import Nominatim
import time
import csv

def reverse_geocode_gpsdatei(
    eingabedatei: str,
    ausgabedatei: str,
    max_dauer_sek: int = 290,
    pause_sek: float = 1.0
) -> None:
    """
    Liest GPS-Koordinaten aus einer CSV-Datei, führt für maximal 4:30 Minuten (270 Sekunden) jede Sekunde eine Reverse-Geocoding-Abfrage durch
    und speichert das Ergebnis (Koordinaten und Straßenname) in einer Ausgabedatei.

    :param eingabedatei: Pfad zur Eingabedatei mit GPS-Daten (CSV)
    :type eingabedatei: str
    :param ausgabedatei: Pfad zur Ausgabedatei für Ergebnisse (CSV)
    :type ausgabedatei: str
    :param max_dauer_sek: Maximale Laufzeit in Sekunden (Standard: 270 = 4:30 min)
    :type max_dauer_sek: int
    :param pause_sek: Pause zwischen den Abfragen in Sekunden (Standard: 1.0)
    :type pause_sek: float
    :returns: None
    :rtype: None
    :raises FileNotFoundError: Wenn die Eingabedatei nicht existiert
    :example:

        >>> reverse_geocode_gpsdatei('GPS2Street.CSV', 'GPS2Street_mit_Strasse.csv')
    """
    geolocator = Nominatim(user_agent="airscout-analytics/1.6 (airscout6@watchkido.de)", timeout=10)
    start_time = time.time()
    anzahl = 0
    with open(eingabedatei, newline='', encoding='utf-8') as csvfile_in, \
         open(ausgabedatei, 'w', newline='', encoding='utf-8') as csvfile_out:
        reader = csv.reader(csvfile_in)
        writer = csv.writer(csvfile_out)
        writer.writerow(['Breite', 'Laenge', 'Strasse'])
        letzter_lat, letzter_lon = None, None
        for row in reader:
            if time.time() - start_time > max_dauer_sek:
                print("Maximale Laufzeit erreicht. Vorgang wird beendet.")
                break
            try:
                lat = float(row[5].strip())
                lon = float(row[6].strip())
            except (IndexError, ValueError):
                # IT-Witz: "GPS-Koordinate nicht gefunden – vielleicht ist sie im Bermuda-Dreieck verschwunden!"
                writer.writerow(['Fehler', 'Fehler', 'Ungültige Zeile'])
                continue
            # Nur abfragen, wenn Koordinate sich geändert hat
            if letzter_lat is not None and letzter_lon is not None:
                if abs(lat - letzter_lat) < 1e-7 and abs(lon - letzter_lon) < 1e-7:
                    # Überspringe doppelte Koordinaten
                    continue
            try:
                # language-Parameter entfernt, da einige geopy-Versionen dies nicht unterstützen
                location = geolocator.reverse((lat, lon), exactly_one=True)
                if location is not None and hasattr(location, 'raw'):
                    street = location.raw.get('address', {}).get('road', 'Unbekannt')
                else:
                    street = 'Unbekannt'
            except Exception as e:
                street = f"Fehler: {e}"
            writer.writerow([lat, lon, street])
            letzter_lat, letzter_lon = lat, lon
            anzahl += 1
            print(f"{anzahl}: {lat}, {lon} -> {street}")
            time.sleep(pause_sek)

if __name__ == "__main__":
    # Starte das Reverse-Geocoding für die Datei GPS2Street.CSV
    reverse_geocode_gpsdatei(
        eingabedatei="e:/dev/projekt_python_venv/airscout-analytics/data/roh/GPS2Street.CSV",
        ausgabedatei="e:/dev/projekt_python_venv/airscout-analytics/data/roh/GPS2Street_mit_Strasse_test.csv",
        max_dauer_sek=270,
        pause_sek=1.0
    )
