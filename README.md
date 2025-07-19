# 🌍 Umweltkontrollsystem – Sensordatenanalyse & Dashboard

Dieses Projekt erfasst und analysiert umfangreiche Umweltdaten, die von einem Arduino Mega 2560 über eine Vielzahl von Sensoren gesammelt werden. Ziel ist ein interaktives Dashboard mit Zeitreihen-, Filter- und Kartendarstellungen zur Visualisierung und Analyse der Messdaten.

---

## 📊 Projektziele

- **Erfassung** von Umweltparametern mit bis zu 100 kHz Abtastrate
- **Zeitreihenanalyse** für Temperatur, Gase, Licht, Geräusche, Strahlung usw.
- **GPS-gestützte Kartendarstellung** der Sensorwerte
- **Filtern & Segmentieren** der Daten nach Ort, Zeit, Messwerten
- **Visualisierung** mit interaktiven Diagrammen (Heatmaps, Scatterplots, Verlaufslinien)
- **Erweiterbares Dashboard** zur Echtzeit- oder nachträglichen Analyse

---

## ⚙️ Tech Stack

- **Python 3.x**
- **Pandas & Numpy** – Datenverarbeitung
- **Matplotlib & Seaborn** – Standardplots
- **Plotly & Dash** oder **Streamlit** – Interaktive Dashboards
- **Geopandas & Folium** – Kartendarstellungen
- **Jupyter Notebooks** – Prototyping & Analyse
- **Git & GitHub** – Versionskontrolle
- **Arduino** – Datenlogger-Hardware

---

## 🗃 Projektstruktur

```plaintext
Umweltkontrollsystem/
│
├── data/                # CSV-Dateien mit Messdaten
├── notebooks/           # Jupyter-Analysen zur Datenexploration
├── dashboard/           # Streamlit- oder Dash-App zur Visualisierung
├── scripts/             # Hilfsskripte für Preprocessing, Datenreinigung, Export
├── assets/              # Kartenmaterial, Bilder, Icons
├── requirements.txt     # Python-Abhängigkeiten
├── .gitignore           # Ausschlussregeln (z. B. .venv, *.pyc)
├── README.md            # Diese Dokumentation
└── .venv/               # Virtuelle Umgebung (nicht ins Git aufnehmen)

## Schnellstart

1. Repository klonen:

   git clone https://github.com/Watchkido/AirScout-Analytics.git
