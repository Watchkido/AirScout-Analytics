
**LUFT- UND UMWELTBERICHT**

**Berichtsdatum:** 27. Juli 2025
**Datenquelle:** `2025_07_12_22_58.csv`
**Erhebungszeitraum:** Hauptsächlich 13. Juli 2025 (basierend auf den Zeitstempeln)

**1. Allgemeine Informationen zur Datenerfassung**
Dieser Bericht basiert auf einer umfangreichen Datenerfassung mit 4207 Einzelmessungen und insgesamt über 180.000 Datenpunkten. Die Datenqualität ist ausgezeichnet, da keine fehlenden Werte oder Duplikate identifiziert wurden, was eine vollständige und zuverlässige Analyse ermöglicht.

**2. Erfasste Umweltparameter**
Die Messungen umfassen eine breite Palette von Umweltfaktoren und Gaskonzentrationen, die ein umfassendes Bild der Umgebung zeichnen:

*   **Klimadaten:** Temperatur und relative Luftfeuchtigkeit.
*   **Lichtverhältnisse:** Lichtstärke (absolut und prozentual).
*   **Geographische Daten:** GPS-Position (Breiten- und Längengrad), Höhe über dem Meeresspiegel, Geschwindigkeit und Kurs.
*   **Akustische Daten:** Zwei Mikrofonsensoren (Mic1, Mic2).
*   **Strahlung:** Geigerzähler (Counts Per Second, CPS).
*   **Luftqualität:** Eine Reihe von MQ-Sensoren zur Erfassung verschiedener Gase und flüchtiger organischer Verbindungen (VOCs).

**3. Zusammenfassung der Messergebnisse**

**3.1. Klimadaten & Lichtverhältnisse**
*   **Temperatur (DHT_C):**
    *   Durchschnitt: 37.46 °C
    *   Minimum: 31.90 °C
    *   Maximum: 48.10 °C
    *   Standardabweichung: 4.94 °C (Hinweis auf Schwankungen)
*   **Relative Luftfeuchtigkeit (Humidity_RH):**
    *   Durchschnitt: 5.83 %
    *   Minimum: 0.00 %
    *   Maximum: 17.00 %
    *   Standardabweichung: 6.79 % (Sehr niedrige durchschnittliche Luftfeuchtigkeit, teils 0% – dies könnte auf Sensorlimitierungen oder extrem trockene Bedingungen hindeuten.)
*   **Licht (Light_Level / Light_Percent):**
    *   Durchschnitt (Level): 24.96
    *   Durchschnitt (Prozent): 97.55 %
    *   Bereich (Level): 6 bis 57
    *   Bereich (Prozent): 94.4 % bis 99.4 % (Zeigt generell helle Bedingungen an)

**3.2. Geographische und Bewegungsparameter**
*   **GPS-Position:** Die Messungen wurden hauptsächlich um die Koordinaten 49.356° N, 8.178° E durchgeführt, was auf einen relativ stationären Messpunkt oder einen kleinen Bewegungsradius hindeutet.
*   **Höhe (GPS_Alt):**
    *   Durchschnitt: 133.12 m
    *   Minimum: 0.00 m (eventuell ein Messfehler oder temporärer GPS-Verlust)
    *   Maximum: 149.10 m
*   **Geschwindigkeit (GPS_Speed):**
    *   Durchschnitt: 0.13 m/s
    *   Maximum: 2.60 m/s (Deutet auf sehr langsame Bewegung oder Stillstand während der meisten Messungen hin.)

**3.3. Strahlungsmessungen**
*   **Strahlung (Radiation_CPS - Counts Per Second):**
    *   Durchschnitt: 3.31 CPS
    *   Minimum: 2 CPS
    *   Maximum: 9 CPS
    *   Standardabweichung: 1.36 CPS (Diese Werte liegen typischerweise im Bereich der natürlichen Hintergrundstrahlung, genaue Bewertung erfordert Referenzwerte.)

**3.4. Luftqualität (Gaskonzentrationen)**
Die MQ-Sensoren messen eine Reihe von Gasen in Parts Per Million (ppm) und Mikrogramm pro Kubikmeter (ug/m³). Die genaue Interpretation der Konzentrationen erfordert spezifische Kalibrierung und Grenzwerte für die jeweilige Anwendung.

*   **MQ2 (Rauch, LPG, Propan, Alkohol, Wasserstoff):**
    *   Durchschnitt: 28.70 ppm (51642.60 ug/m³)
    *   Bereich: 26.15 - 31.62 ppm (47059.30 - 56903.07 ug/m³)
*   **MQ3 (Alkohol, Ethanol, Rauch):**
    *   Durchschnitt: 18.73 ppm (35247.37 ug/m³)
    *   Bereich: 17.98 - 19.95 ppm (33827.40 - 37533.74 ug/m³)
*   **MQ4 (Methan, Erdgas, LPG):**
    *   Durchschnitt: 13.98 ppm (9150.05 ug/m³)
    *   Bereich: 13.62 - 14.72 ppm (8912.88 - 9632.72 ug/m³)
*   **MQ5 (LPG, Erdgas, Kohlegas):**
    *   Durchschnitt: 15.80 ppm (28435.56 ug/m³)
    *   Bereich: 15.40 - 16.72 ppm (27713.70 - 30089.16 ug/m³)
*   **MQ6 (LPG, Butan, Propan):**
    *   Durchschnitt: 18.00 ppm (32387.58 ug/m³)
    *   Bereich: 17.39 - 19.29 ppm (31294.89 - 34714.11 ug/m³)
*   **MQ7 (Kohlenmonoxid CO):**
    *   Durchschnitt: 3.28 ppm (3754.28 ug/m³)
    *   Bereich: 3.14 - 3.54 ppm (3595.91 - 4053.99 ug/m³)
    *   *Anmerkung: Kohlenmonoxid ist ein toxisches Gas. Diese Werte sollten im Kontext von Gesundheitsrichtlinien bewertet werden.*
*   **MQ8 (Wasserstoff H2):**
    *   Durchschnitt: 13.71 ppm (1121.49 ug/m³)
    *   Bereich: 13.33 - 14.38 ppm (1090.39 - 1176.28 ug/m³)
*   **MQ9 (Kohlenmonoxid CO, brennbare Gase):**
    *   Durchschnitt: 4.69 ppm (5375.52 ug/m³)
    *   Bereich: 4.56 - 4.95 ppm (5222.09 - 5668.71 ug/m³)
    *   *Anmerkung: Auch hier ist die CO-Komponente relevant für die Bewertung der Luftqualität.*
*   **MQ135 (VOCs, CO2, Benzol, Alkohol, Rauch):**
    *   Durchschnitt: 1.21 ppm (2271.28 ug/m³)
    *   Bereich: 1.18 - 1.28 ppm (2220.04 - 2408.18 ug/m³)
    *   *Anmerkung: Dieser Sensor ist breitbandig und reagiert auf verschiedene Verunreinigungen, einschließlich CO2-Äquivalente und flüchtige organische Verbindungen, die auf die allgemeine Luftqualität hinweisen.*

**4. Auffällige Korrelationen**
Der Bericht zeigt interessante Korrelationen zwischen den Messgrößen:
*   **Temperatur, Luftfeuchtigkeit und Licht:** Es besteht eine hohe inverse Korrelation zwischen Temperatur und Luftfeuchtigkeit (-0.739), sowie Temperatur und Lichtlevel (-0.781). Das bedeutet, dass mit steigender Temperatur die Luftfeuchtigkeit und das Lichtlevel tendenziell abnehmen. Dies könnte saisonale oder tageszeitliche Effekte widerspiegeln.
*   **Temperatur und MQ7 (CO):** Eine hohe positive Korrelation zwischen Temperatur und dem Rohwert von MQ7 (0.836) sowie eine negative Korrelation zur umgerechneten ppm-Konzentration (-0.820) ist zu beobachten. Dies deutet darauf hin, dass die Temperatur einen signifikanten Einfluss auf die Sensorreaktion oder die tatsächliche CO-Konzentration hat.
*   **MQ-Sensoren untereinander:** Viele MQ-Sensoren zeigen sehr hohe positive Korrelationen untereinander (z.B. MQ4 mit MQ5, MQ6, MQ7, MQ8; MQ3 mit MQ9 und MQ135). Dies ist typisch, da viele dieser Sensoren eine gewisse Kreuzempfindlichkeit aufweisen oder auf ähnliche allgemeine Luftveränderungen reagieren.

**5. Schlussfolgerung**
Der vorliegende Datensatz bietet eine solide Grundlage für die Analyse der Luft- und Umweltbedingungen am Messort. Die erfassten Daten sind vollständig und weisen keine Lücken auf. Insbesondere die detaillierten Gaskonzentrationen, zusammen mit Temperatur, Feuchtigkeit und Strahlung, ermöglichen eine umfassende Bewertung der lokalen Umweltqualität.

Für eine tiefere Interpretation der Luftqualität sind Referenzwerte und Grenzwerte relevanter Behörden (z.B. Umweltbundesamt) für die jeweiligen Gase notwendig. Die festgestellten Korrelationen bieten Ansatzpunkte für weitere Untersuchungen, um die Wechselwirkungen zwischen den verschiedenen Umweltfaktoren und Gaskonzentrationen besser zu verstehen.
