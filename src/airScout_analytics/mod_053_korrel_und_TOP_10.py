


    """
    Pipeline-kompatibler Einstiegspunkt für die Korrelationen- und Top-10%-Analyse.
    """
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import os
    import sys
    import glob
    import warnings
    warnings.filterwarnings("ignore", category=FutureWarning)
    warnings.filterwarnings("ignore", category=UserWarning)
    warnings.filterwarnings("ignore", category=Warning)
    import airScout_analytics.context as context
    # === Automatische Auswahl der ersten CSV aus bearbeitet3 ===
    datenordner = os.path.join("data", "bearbeitet3")
    csv_dateien = glob.glob(os.path.join(datenordner, "*.csv"))
    if not csv_dateien:
        print(f"Keine CSV-Dateien in {datenordner} gefunden.")
        return
    pfad = csv_dateien[0]
    # === 2. CSV-Datei laden ===
    try:
        df = pd.read_csv(pfad, comment="#")
        print("Datei erfolgreich geladen.")
    except FileNotFoundError:
        print("Datei nicht gefunden. Bitte stelle sicher, dass sie im Download-Ordner liegt.")
        return
    # GPS-Spalten in float konvertieren
    for gps_col in ["GPS_Lat", "GPS_Lon"]:
        if gps_col in df.columns:
            df[gps_col] = pd.to_numeric(df[gps_col], errors="coerce")
    # Zeilen mit fehlenden Werten entfernen
    df = df.dropna()
    # Die ersten 10 Minuten (600 Sekunden) jedes Datensatzes entfernen
    if "SecSinceMidnight-MS" in df.columns:
        df["_sec"] = df["SecSinceMidnight-MS"].astype(str).str.split("-").str[0].astype(float)
        df = df[df["_sec"] > 600]
        df = df.drop(columns=["_sec"])
    # === 3. Zeitstempel in datetime umwandeln ===
    datetime_spalte = None
    for col in df.columns:
        if col.startswith("DateTime"):
            datetime_spalte = col
            break
    if not datetime_spalte:
        for col in df.columns:
            if "DateTime" in col:
                datetime_spalte = col
                break
    if not datetime_spalte:
        print("Keine DateTime-Spalte gefunden! Verfügbare Spalten:", list(df.columns))
        return
    df["DateTime"] = pd.to_datetime(df[datetime_spalte].str.replace(r" MESZ| UTC", "", regex=True), errors="coerce")
    # === 4. Gassensoren definieren ===
    gassensoren = ["MQ2", "MQ3", "MQ4", "MQ5", "MQ6", "MQ7", "MQ8", "MQ9", "MQ135"]
    # === 5. Plot: Gassensorverlauf ===
    zeitachsen = [col for col in ["DateTime", "GPS_DateTime"] if col in df.columns]
    if zeitachsen:
        zeit_col = zeitachsen[0]
    else:
        zeit_col = None
    if zeit_col:
        fig, ax1 = plt.subplots(figsize=(14, 7))
        plotted = False
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
            umwelt_datei = os.path.expanduser(f"~/Downloads/umweltwerte_{context.filename_ohne_ext}.png")
            plt.savefig(umwelt_datei)
            plt.close(fig)
            print(f"Umweltwerte-Diagramm (log10, >50) gespeichert als '{umwelt_datei}'.")
        else:
            print("Warnung: Keine Werte > 50 für Temperatur, Feuchte oder Radioaktivität zum log-Plotten vorhanden.")
    else:
        print("Keine geeignete Zeitspalte (DateTime oder GPS_DateTime) für das Umweltwerte-Diagramm gefunden.")
    # === MQ135 Luftqualitätsbewertung und Top-10%-Karte ===
    mq135_werte = df["MQ135"].dropna()
    q1 = mq135_werte.quantile(0.25)
    q3 = mq135_werte.quantile(0.75)
    def luftqualitaet_index(wert: float) -> str:
        if wert < q1:
            return "Gut"
        elif wert < q3:
            return "Mäßig"
        else:
            return "Schlecht"
    if "MQ135" in df.columns:
        print(f"Luftqualitäts-Schwellenwerte: Q1 = {q1:.2f}, Q3 = {q3:.2f}")
        df["Luftqualitaet"] = df["MQ135"].apply(luftqualitaet_index)
        print("Letzte 5 Bewertungen der Luftqualität:")
        print(df[["DateTime", "MQ135", "Luftqualitaet"]].tail())
        try:
            import folium
            sensor_colors = {
                "MQ2": "red",
                "MQ3": "orange",
                "MQ4": "green",
                "MQ5": "blue",
                "MQ6": "purple",
                "MQ7": "darkred",
                "MQ8": "darkblue",
                "MQ9": "cadetblue",
                "MQ135": "black"
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
            df_gps = df[df["GPS_Lat"].notna() & df["GPS_Lon"].notna()]
            if not df_gps.empty:
                lat_mittel = df_gps["GPS_Lat"].mean()
                lon_mittel = df_gps["GPS_Lon"].mean()
                m = folium.Map(location=[lat_mittel, lon_mittel], zoom_start=12)
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
                legend_html = '<div style="position: fixed; bottom: 50px; left: 50px; width: 450px; height: 260px; z-index:9999; font-size:14px; background: white; border:2px solid grey; padding: 10px;">'
                legend_html += '<b>Legende: Sensorfarben und Gase</b><br>'
                for sensor, farbe in sensor_colors.items():
                    legend_html += f'<i style="background:{farbe};color:{farbe};border-radius:50%;padding:4px 8px;margin-right:8px;">●</i> <b>{sensor}</b>: {sensor_gas[sensor]}<br>'
                legend_html += '</div>'
                ergebnisse_dir = os.path.join("data", "ergebnisse")
                unterordner = os.path.join(ergebnisse_dir, context.filename_ohne_ext)
                os.makedirs(ergebnisse_dir, exist_ok=True)
                os.makedirs(unterordner, exist_ok=True)
                map_datei1 = os.path.join(ergebnisse_dir, f"sensor_top10_map_{context.filename_ohne_ext}.html")
                map_datei2 = os.path.join(unterordner, f"sensor_top10_map_{context.filename_ohne_ext}.html")
                m.get_root().html.add_child(folium.Element(legend_html))
                m.save(map_datei1)
                m.save(map_datei2)
                print(f"Karte mit den 10% höchsten Werten aller Sensoren gespeichert als '{map_datei1}' und '{map_datei2}'.")
            else:
                print("Keine gültigen GPS-Daten gefunden.")
        except ImportError:
            print("Das Paket 'folium' ist nicht installiert. Bitte mit 'pip install folium' nachinstallieren.")
    # === 8. Korrelationen anzeigen ===
    import seaborn as sns
    zusatzsensoren = [
        "Temperatur", "Temp", "Hygrometer", "Feuchtigkeit", "Radioaktivität", "Radioaktivitaet", "Licht", "Light"
    ]
    korrelations_spalten = [s for s in gassensoren if s in df.columns]
    for zusatz in zusatzsensoren:
        if zusatz in df.columns and zusatz not in korrelations_spalten:
            korrelations_spalten.append(zusatz)
    korrelationen = df[korrelations_spalten].corr()
    plt.figure(figsize=(10, 8))
    ax = sns.heatmap(korrelationen, annot=True, cmap="coolwarm", fmt=".2f")
    plt.title("Korrelationsmatrix der Gassensoren")
    legende = "\n".join([f"{s}: {sensor_gas[s]}" for s in gassensoren if s in df.columns])
    plt.gcf().text(0.01, -0.01, "Gase je Sensor:", ha='left', va='top', fontsize=15, fontweight='bold')
    plt.gcf().text(0.01, -0.06, legende, ha='left', va='top', fontsize=12)
    plt.tight_layout(rect=(0,0.08,1,1))
    ergebnisse_dir = os.path.join("data", "ergebnisse")
    unterordner = os.path.join(ergebnisse_dir, context.filename_ohne_ext)
    os.makedirs(ergebnisse_dir, exist_ok=True)
    os.makedirs(unterordner, exist_ok=True)
    korrelationsgrafik_datei1 = os.path.join(ergebnisse_dir, f"korrelationsmatrix_{context.filename_ohne_ext}.png")
    korrelationsgrafik_datei2 = os.path.join(unterordner, f"korrelationsmatrix_{context.filename_ohne_ext}.png")
    plt.savefig(korrelationsgrafik_datei1, bbox_inches='tight')
    plt.savefig(korrelationsgrafik_datei2, bbox_inches='tight')
    plt.close()
    print(f"Korrelationsgrafik gespeichert als '{korrelationsgrafik_datei1}' und '{korrelationsgrafik_datei2}'.")
    print("\nAnalyse abgeschlossen.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Fehler bei der Korrelation/Top-10-Analyse: {e}")
            map_datei2 = os.path.join(unterordner, f"sensor_top10_map_{context.filename_ohne_ext}.html")
