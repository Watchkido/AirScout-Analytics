# 🌍 AirScout-Analytics

## Umweltkontrollsystem – Sensordatenanalyse & Dashboard

Dieses Projekt erfasst und analysiert umfangreiche [Umweltdaten](https://www.kaggle.com/datasets/avitarus/hyperlocal-urban-environmental-monitoring-dataset) aus Neustadt an der Weinstrasse (Juli 2025), die von einem [Arduino Mega 2560](https://github.com/Watchkido/AirScout-Firmware) über eine Vielzahl von Sensoren gesammelt werden. Ziel ist ein interaktives Dashboard mit Zeitreihen-, Filter- und Kartendarstellungen zur Visualisierung und Analyse der Messdaten.

<iframe src="https://www.komoot.com/de-de/tour/2413578613/embed?share_token=apHyFIhrf2YKNJ2b1SoPXXkasVKoAAOQN9jk74EsBOb3qIL1sM&profile=1" width="100%" height="700" frameborder="0" scrolling="no"></iframe>


![AirScout-One](img/airscoutone.jpg)

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

## 🧠 Kernfunktionen
### 1. Automatisierte Datenpipeline
```mermaid
graph TD
    A[CSV-Rohdaten] --> B(Data Cleaning)
    B --> C{Analyse-Modus}
    C -->|Standard| D[Grafische Auswertung]
    C -->|Expert| E[Machine Learning]
    D --> F[PDF-Report]
    E --> F
```

### 2. Wichtige Skripte
| Skript | Beschreibung | Output |
|--------|-------------|--------|
| `csv_analyser.py` | Hauptpipeline (Datenanalyse + Visuals) | HTML/PDF |
| `geo_mapper.py` | Interaktive Pollution-Maps | GeoJSON |
| `report_generator.py` | Autom. Report-Erstellung | PDF |

---


### 📈 Visualisierung
![Dashboard](images/dashboard_preview.png)

---

## 📝 Prüfungsrelevante Aspekte
1. **Software-Engineering**:
   - MVC-Architektur
   - Unit-Tests (pytest)
   - CI/CD (GitHub Actions)

2. **Data Science**:
   - Zeitreihenanalyse
   - Geospatiale Visualisierung
   - Signalverarbeitung (Audio)

---

## 🧪 Testprotokoll
```bash
pytest tests/ --cov=src/ --cov-report=html
```
| Modul | Abdeckung | Status |
|-------|-----------|--------|
| Datenbereinigung | 0% | ❌ |
| Geo-Mapping | 0% | ❌ |
| Report-Gen | 0% | ❌ |

---

## 📜 Lizenz & Danksagung
**MIT License** - Speziell entwickelt für die Python-Prüfung 2025.  
*Betreut durch [Institut/Professor]*  

**Kontakt:**  
Frank Albrecht | [airscout@watchkido.de](mailto:airscout@watchkido.de)  

## Schnellstart

1. Repository klonen:

   git clone https://github.com/Watchkido/python_projekt_generator.git
