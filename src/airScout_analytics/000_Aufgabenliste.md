
### **Projekt: Luftqualitätsanalyse für Bürger - 3-Tages-Sprintplan**

**Tag 1: Datenaufbereitung & Erste Analyse**

Dein Hauptziel heute ist es, die Rohdaten zu verstehen, zu bereinigen und erste Transformationen durchzuführen.

*   **1.1 Datenimport & Grundlegende Inspektion:**
    *   Lade alle Sensordaten (GPS, Temperatur/Feuchtigkeit, MQ-Sensoren, Licht, ggf. Strahlung) in Pandas DataFrames.
    *   Überprüfe die Daten auf fehlende Werte (`df.isnull().sum()`) und entscheide über eine Strategie (z.B. `fillna`, `dropna`, Interpolation).
    *   Konvertiere die Zeitstempelspalte(n) in das `datetime`-Format, falls noch nicht geschehen (`pd.to_datetime()`).
*   **1.2 Erste Visualisierung der Rohdaten:**
    *   Plot (Zeitreihen-Diagramm) der wichtigsten Sensoren (z.B. MQ135, Temperatur, GPS_Speed) über die Zeit, um Trends, Rauschen und offensichtliche Ausreißer zu identifizieren.
    *   **Achte besonders auf:** Schwankungen der MQ-Sensoren und ob diese mit Temperatur-/Feuchtigkeitsänderungen korrelieren, wie in den Quellen erwähnt.
*   **1.3 Implementierung einfacher Glättung:**
    *   Wende einen **gleitenden Mittelwert** (`.rolling().mean()`) auf deine Haupt-Sensordaten (insbesondere die MQ-Werte) an. Dies hilft, Rauschen zu reduzieren und die Ablesbarkeit zu verbessern. Experimentiere mit verschiedenen Fenstergrößen.

---

**Tag 2: Feature Engineering & Sensorkompensation (Der Herzstück des Projekts)**

Heute steht die Veredelung deiner Daten im Vordergrund, um aussagekräftigere Informationen zu erhalten. Die Kompensation der Gassensoren ist hierbei entscheidend!

*   **2.1 Temperatur- und Feuchtigkeitskompensation der MQ-Sensoren (Sehr wichtig!):**
    *   **Stelle sicher, dass du Temperatur- und Feuchtigkeitsdaten vorliegen hast**; dies ist der Schlüssel für genaue MQ-Sensorwerte.
    *   Implementiere einen **vereinfachten Kompensationsansatz** wie im Pseudocode beschrieben. Du musst hierfür `temp_sensitivitaetsfaktor` und `feuchtigkeits_sensitivitaetsfaktor` entweder durch Recherche im Datenblatt deiner MQ-Sensoren oder durch Annahmen ermitteln. Dies transformiert Rohwerte in "bereinigte" Gaskonzentrationen.
    *   **Alternativ/Zusätzlich:** Berechne den `mq7_co_baseline_ratio` oder ähnliche normalisierte Werte, um relative Veränderungen zu zeigen.
*   **2.2 Berechnung von Key Performance Indicators (KPIs):**
    *   Implementiere ausgewählte **Bewegungs-KPIs**:
        *   `Gesamte zurückgelegte Strecke` (Summe der `distanz_seit_letztem_punkt_m`).
        *   `Durchschnittsgeschwindigkeit`.
        *   `Anzahl der Stopps`.
    *   Implementiere **Luftqualitäts-KPIs**:
        *   `Maximale Gas-Konzentration` pro Sensor (z.B. `MAX(MQ2)`, `MAX(MQ135)`).
        *   `Durchschnittliche Belastung` (`AVG(MQ135)`).
*   **2.3 Erstellung von weiteren Features (Auswahl treffen):**
    *   Füge folgende berechnete Spalten hinzu:
        *   `distanz_seit_letztem_punkt_m` mithilfe der Haversine-Formel.
        *   `is_stillstand` (TRUE, wenn GPS_Speed < 0.5 km/h).
        *   `luftqualitaet_spike` (statistische Anomalieerkennung, z.B. Wert > Mittelwert + 3 * Standardabweichung).
        *   `ist_verkehrsstau` (Kombination aus `is_stillstand` für > 1 min UND ansteigendem `AVG(MQ135)`).
        *   Wähle optional weitere Features, die für dich besonders relevant erscheinen (z.B. `rollender_max_mq2_rauch`).

---

**Tag 3: Analyse, Visualisierung & Kommunikation der Ergebnisse**

Heute geht es darum, die gewonnenen Erkenntnisse aufzubereiten und in einer verständlichen Form zu präsentieren, die einen direkten Nutzen für den Bürger bietet.

*   **3.1 Analyse der aufbereiteten Daten:**
    *   **Lokaler Bezug:** Identifiziere mithilfe deiner GPS-Daten und der Luftqualitätsdaten Abschnitte oder Orte (z.B. Kreuzungen, Spielplätze), an denen die Luftqualität besonders schlecht ist.
    *   **Zusammenhänge aufdecken:** Analysiere, ob `ist_verkehrsstau` tatsächlich mit erhöhten MQ-Werten (insbesondere MQ7 für CO und MQ135) korreliert.
    *   **Anomalien identifizieren:** Untersuche die `luftqualitaet_spike`-Ereignisse – wann und wo treten sie auf, und gibt es Muster?
*   **3.2 Erstellung aussagekräftiger Visualisierungen:**
    *   **Luftqualitäts-Karte:** Erstelle eine einfache Karte (z.B. mit Folium oder Geopandas, falls Koordinaten verfügbar sind), die die Luftqualität (z.B. mittels **Ampelfarben: grün=gut, gelb=mittel, rot=schlecht**) an verschiedenen Punkten deiner Route anzeigt.
    *   **Zeitreihen-Plots:** Zeige den Verlauf der kompensierten MQ-Werte über die Zeit, eventuell kombiniert mit Bewegungsmustern (`is_stillstand`).
    *   **Übersicht der KPIs:** Präsentiere die berechneten KPIs übersichtlich (z.B. höchste Belastung durch X in Y-Gebiet).
*   **3.3 Aufbereitung der Ergebnisse für Bürger (Die Botschaft!):**
    *   **Vergiss Fachbegriffe und komplexe Diagramme!** Sprich, als würdest du es deinem Nachbarn beim Grillen erklären.
    *   **Fokus auf konkrete Vorteile für MICH:** Erkläre, wie deine Arbeit die **Gesundheit und Sicherheit von Kindern** beeinflusst und **Auswirkungen auf den Alltag** hat.
    *   **Beispiele für Formulierungen:**
        *   "Ich habe ein Gerät gebaut, das uns zeigt, ob die Luft, die wir atmen, uns krank machen könnte."
        *   "Stell dir vor, du könntest auf einer einfachen Karte sehen, ob es heute sicher ist, mit den Kindern auf dem Spielplatz zu toben."
        *   "Es ist wie eine Wettervorhersage für die Luftqualität. So wie du siehst, ob es regnet, siehst du, ob die Luft gut oder schlecht ist."
    *   **Das "Warum" und "Was jetzt?":** Erkläre, warum schlechte Luft wichtig ist (Asthma, Krankheiten bei Kindern) und was getan werden kann ("Wir können endlich sehen, wo wir handeln müssen").
    *   **Transparenz und Vertrauen:** Erkläre, wie die Messungen zustande kommen und wie man sie nachvollziehen kann.
    *   **Lokaler Bezug:** Hebe hervor, ob die Messungen für das Viertel oder den Kindergarten spezifisch sind.

---

**Wichtige Hinweise für die 3 Tage:**

*   **Fokus auf das Wesentliche:** Die Quellen bieten viele fortgeschrittene Konzepte (z.B. Maschinelles Lernen für Kompensation, Kalman-Filter). Für 3 Tage solltest du dich auf die **Grundlagen** und die **am direktesten anwendbaren Methoden** konzentrieren. Eine **vereinfachte Temperatur- und Feuchtigkeitskompensation** ist besser als keine.
*   **Iteratives Vorgehen:** Gehe die Schritte sequenziell durch. Wenn ein Schritt zu viel Zeit in Anspruch nimmt, vereinfache ihn, um das Gesamtziel nicht zu gefährden.
*   **Code-Organisation:** Halte deinen Python-Code sauber und kommentiert.
*   **Datensatz:** Dieser Plan geht davon aus, dass du bereits einen gesammelten Sensordatensatz hast. Die Qualität und Vollständigkeit dieses Datensatzes werden deinen Fortschritt maßgeblich beeinflussen.

Viel Erfolg bei deinem Abschlussprojekt!

