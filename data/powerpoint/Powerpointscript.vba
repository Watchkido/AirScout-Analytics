Sub CreateForensicPresentation_Fixed()
    Dim ppt As Presentation
    Dim sld As Slide
    Dim shp As Shape
    Dim menuItems As Variant
    Dim sectionIndex As Long
    Dim scoresM As Long, scoresR As Long
    
    ' Präsentation neu erstellen
    Set ppt = Application.Presentations.Add
    
    ' Left-Navi-Menü-Beschriftungen
    menuItems = Array("START", "Die Pipeline", "Laden und reinigen", "CSV Analyser", _
                      "Beweis A", "Beweis B", "Beweis C", "Beweis D", _
                      "Versuch", "Erkenntnis", "Urteil", "Beweiskette", "Empfehlung", "Q&A", "A1-1", "A1-2", "A2-1", "A2-2")
    
    scoresM = 0
    scoresR = 0
    
' =========================================================================
' *** SCHLEIFE 1: FOLIEN MIT ALLEN ANPASSUNGEN ERSTELLEN ***
' =========================================================================
For sectionIndex = LBound(menuItems) To UBound(menuItems)
    ' Folie erstellen und benennen
    Set sld = ppt.Slides.Add(sectionIndex + 1, 2)
    sld.Name = "Slide_ID_" & sld.SlideID
    
    ' Score-Werte aktualisieren
    Select Case sectionIndex + 1
        Case 5: scoresM = 3
        Case 6: scoresM = 8
        Case 7: scoresM = 11
        Case 8: scoresM = 15
    End Select
    
    ' --- A) TITEL-BEREICH GESTALTEN (Titel + Score-Tafel) ---
    Dim titleShape As Shape
    Set titleShape = sld.Shapes.Title
    titleShape.TextFrame.TextRange.Text = GetSlideTitle(sectionIndex + 1)
    
    ' Nur auf Folien nach der Startfolie anwenden
    If sectionIndex > 0 Then
        ' 1. Titel nach links rücken und Platz für Score-Tafel schaffen
        titleShape.Left = 150 ' Titel beginnt weiter links
        Dim scoreAreaWidth As Single
        scoreAreaWidth = titleShape.Width * 0.2 ' Breite für Score-Tafel
        titleShape.Width = titleShape.Width - scoreAreaWidth - 60 ' Breite des Titels anpassen
        
        ' 2. Score-Tafel rechts neben dem Titel erstellen
        Dim scoreL, scoreT, scoreH As Single
        scoreL = titleShape.Left + titleShape.Width + 10
        scoreT = titleShape.Top
        scoreH = titleShape.Height
        
        ' Hintergrund für die Tafel
        Dim scoreBg As Shape
        Set scoreBg = sld.Shapes.AddShape(msoShapeRectangle, scoreL, scoreT, scoreAreaWidth, scoreH)
        With scoreBg
            .Fill.ForeColor.RGB = RGB(40, 40, 40)
            .Line.Visible = msoFalse
        End With
        
        ' M-Score und R-Score Boxen
        Dim mScoreBox As Shape, rScoreBox As Shape, boxWidth As Single
        boxWidth = (scoreAreaWidth / 2) - 5
        
        ' M-Score
        Set mScoreBox = sld.Shapes.AddTextbox(msoTextOrientationHorizontal, scoreL + 5, scoreT, boxWidth, scoreH)
        With mScoreBox.TextFrame.TextRange
            .Text = scoresM & vbCrLf & "MOCK"
            .Paragraphs(1).Font.Size = 55
            .Paragraphs(1).Font.Bold = msoTrue
            .Paragraphs(2).Font.Size = 18
            .Font.Color.RGB = RGB(50, 255, 50) ' Leuchtendes, "giftiges" Grün
            .ParagraphFormat.Alignment = ppAlignCenter
        End With
        
        ' R-Score
        Set rScoreBox = sld.Shapes.AddTextbox(msoTextOrientationHorizontal, scoreL + boxWidth + 5, scoreT, boxWidth, scoreH)
        With rScoreBox.TextFrame.TextRange
            .Text = scoresR & vbCrLf & "REAL"
            .Paragraphs(1).Font.Size = 55
            .Paragraphs(1).Font.Bold = msoTrue
            .Paragraphs(2).Font.Size = 18
            .Font.Color.RGB = RGB(255, 0, 0) ' Intensives, reines "Alarm"-Rot
            .ParagraphFormat.Alignment = ppAlignCenter
        End With
    End If
    
    ' --- B) HAUPTINHALTS-BEREICH GESTALTEN (Text links, Grafik rechts) ---
    Dim contentShape As Shape
    Set contentShape = sld.Shapes.Placeholders(2)
    contentShape.TextFrame.TextRange.Text = GetSlideContent(sectionIndex + 1, scoresM, scoresR)
    
    
    ' =========================================================
' === NEU HINZUGEFÜGT: SCHRIFTART FÜR DAS TEXTFELD ÄNDERN ===
' =========================================================
With contentShape.TextFrame.TextRange.Font
    .Name = "Arial"      ' <-- ÄNDERN: Schriftart (z.B. "Calibri", "Arial")
    .Size = 18           ' <-- ÄNDERN: Schriftgröße
    .Color.RGB = RGB(0, 0, 0) ' <-- ÄNDERN: Schriftfarbe (hier: Schwarz)
    .Bold = msoFalse     ' <-- ÄNDERN: Fett (msoTrue) oder nicht (msoFalse)
End With
' =========================================================
' === ENDE DER NEUEN ZEILEN ===============================
' =========================================================
    
    
    
    ' Nur auf Folien nach der Startfolie anwenden
    If sectionIndex > 0 Then
        ' 1. Textfeld nach links rücken und halbieren
        Dim origWidth As Single
        origWidth = contentShape.Width
        contentShape.Left = 150 ' Text beginnt weiter links
        contentShape.Width = (origWidth / 2) - 20 ' Breite auf ca. die Hälfte reduzieren
        
        ' 2. Platzhalter für Grafik rechts daneben hinzufügen
        Dim graphicLeft As Single, graphicTop As Single, graphicWidth As Single, graphicHeight As Single
        graphicLeft = contentShape.Left + contentShape.Width + 20
        graphicTop = contentShape.Top
        graphicWidth = origWidth / 2
        graphicHeight = contentShape.Height

        Dim graphicPlaceholder As Shape
        Set graphicPlaceholder = sld.Shapes.AddShape(msoShapeRectangle, graphicLeft, graphicTop, graphicWidth, graphicHeight)
        With graphicPlaceholder
             .Fill.ForeColor.RGB = RGB(245, 245, 245)
             .Line.DashStyle = msoLineDash
             .Line.ForeColor.RGB = RGB(180, 180, 180)
             With .TextFrame
                 .TextRange.Text = "Grafik hier einfügen"
                 .VerticalAnchor = msoAnchorMiddle
                 .HorizontalAnchor = msoAnchorCenter
                 .TextRange.Font.Color.RGB = RGB(150, 150, 150)
                 .TextRange.Font.Size = 14
             End With
        End With
    End If
    
    ' --- C) FUSSZEILE UND NOTIZEN (unverändert) ---
    If sectionIndex > 0 Then
        With sld.HeadersFooters
            .Footer.Visible = msoTrue
            .Footer.Text = "Frank Albrecht | Datenanalyst | Abteilung: IT-Sicherheit | 05.06.2025 | Deutsche Bank"
            .DateAndTime.Visible = msoFalse
            .SlideNumber.Visible = msoFalse
        End With
    End If
    
    If sld.NotesPage.Shapes.Placeholders.Count >= 2 Then
        sld.NotesPage.Shapes.Placeholders(2).TextFrame.TextRange.Text = GetSlideNotes(sectionIndex + 1)
    End If
    
Next sectionIndex
    
    
' =========================================================================
' *** SCHLEIFE 2: NAVIGATIONSMENÜ ALS GRAFISCHE BUTTONS HINZUFÜGEN ***
' =========================================================================
' Jetzt existieren alle Folien, daher werden die Hyperlinks funktionieren.

' -- Definieren Sie hier Ihr Farbschema für die Buttons --
Dim activeFillColor As Long, normalFillColor As Long
Dim activeFontColor As Long, normalFontColor As Long, borderColor As Long

' Professionelles Blau/Grau-Schema
activeFillColor = RGB(0, 80, 150)       ' Dunkelblau für den aktiven Button
normalFillColor = RGB(240, 240, 240)     ' Hellgrau für normale Buttons
activeFontColor = RGB(255, 255, 255)     ' Weißer Text für den aktiven Button
normalFontColor = RGB(30, 30, 30)        ' Dunkelgrauer Text für normale Buttons
borderColor = RGB(180, 180, 180)       ' Ein unauffälliger Rand

' -- Schleife zum Erstellen der Buttons auf jeder Folie --
For sectionIndex = 0 To UBound(menuItems)
    Set sld = ppt.Slides(sectionIndex + 1)
    
    Dim i As Integer, yt As Single
    Dim buttonHeight As Single, buttonSpacing As Single
    ' *** HIER ÄNDERN (Punkt 3): HÖHE & ABSTAND *** ??
    ' Verringern Sie diese Werte, damit alle Buttons auf die Folie passen.
    buttonHeight = 22
    buttonSpacing = 3
    yt = 40 ' Startposition von oben
    
    For i = 0 To UBound(menuItems)
        ' Erstellt ein Rechteck mit abgerundeten Ecken als Button
                '   Erstellt ein Rechteck mit abgerundeten Ecken als Button
        '                                                      Breite|Höhe
        '                                                         v     v
        Set shp = sld.Shapes.AddShape(msoShapeRoundedRectangle, 10, yt, 115, buttonHeight)
        
        With shp
            ' --- Allgemeine Stile für ALLE Buttons ---
            .Line.ForeColor.RGB = borderColor
            .Line.Weight = 0.75
            .Shadow.Type = msoShadow21 ' Dezenter Schatten unten rechts
            
            ' --- Textformatierung ---
            With .TextFrame
                .HorizontalAnchor = msoAnchorCenter ' Text horizontal zentrieren
                .VerticalAnchor = msoAnchorMiddle   ' Text vertikal zentrieren
                .TextRange.Text = menuItems(i)
                .TextRange.Font.Name = "Calibri"
            ' --- HIER ÄNDERN (Punkt 1): SCHRIFTGRÖSSE *** ??
                .TextRange.Font.Size = 11
            End With
            
            ' --- Spezifische Stile für AKTIVEN vs. NORMALEN Button ---
            If i = sectionIndex Then
                ' Dies ist der aktive Button
                .Fill.ForeColor.RGB = activeFillColor
                .TextFrame.TextRange.Font.Color.RGB = activeFontColor
                .TextFrame.TextRange.Font.Bold = msoTrue
            Else
                ' Dies ist ein normaler, inaktiver Button
                .Fill.ForeColor.RGB = normalFillColor
                .TextFrame.TextRange.Font.Color.RGB = normalFontColor
                .TextFrame.TextRange.Font.Bold = msoFalse
            End If

            ' --- Hyperlink hinzufügen (unverändert) ---
            With .ActionSettings(ppMouseClick)
                .Action = ppActionHyperlink
                .Hyperlink.Address = ""
                .Hyperlink.SubAddress = ppt.Slides(i + 1).Name
            End With
        End With
        
        yt = yt + buttonHeight + buttonSpacing ' Nächste Position berechnen
    Next i
Next sectionIndex

    
    ' Speichern der Präsentation
    On Error Resume Next
    Dim savePath As String
    savePath = ActivePresentation.Path
    If savePath = "" Then savePath = Environ("USERPROFILE") & "\Desktop" ' Fallback auf Desktop
    On Error GoTo 0
    
    ppt.SaveAs savePath & "\Forensic_Analyse.pptx"
    MsgBox "Präsentation erstellt und gespeichert als '" & savePath & "\Forensic_Analyse.pptx'", vbInformation

End Sub

' --- HELFER-FUNKTIONEN (unverändert, waren bereits korrekt) ---

Function GetSlideTitle(idx As Long) As String
    Select Case idx
        Case 1: GetSlideTitle = "Titel 1"
        Case 2: GetSlideTitle = "Titel 2"
        Case 3: GetSlideTitle = "Titel 3"
        Case 4: GetSlideTitle = "Titel 4"
        Case 5: GetSlideTitle = "Titel 5"
        Case 6: GetSlideTitle = "Titel 6"
        Case 7: GetSlideTitle = "Titel 7"
        Case 8: GetSlideTitle = "Titel 8"
        Case 9: GetSlideTitle = "Titel 9"
        Case 10: GetSlideTitle = "Titel 10"
        Case 11: GetSlideTitle = "Titel 11"
        Case 12: GetSlideTitle = "Titel 12"
        Case 13: GetSlideTitle = "Titel 13"
        Case 14: GetSlideTitle = "Titel 14"
        Case 15: GetSlideTitle = "Titel 15"
        Case 16: GetSlideTitle = "Titel 16"
        Case 17: GetSlideTitle = "Titel 17"
        Case 18: GetSlideTitle = "Titel 18"
    End Select
End Function

Function GetSlideContent(idx As Long, m As Long, r As Long) As String
    Select Case idx
        Case 1
            GetSlideContent = "Analyse des Datensatzes: Bewertung der Authentizität & Implikationen" & vbCrLf & _
                              "Untertitel: Eine forensische Datenanalyse für den IT-Vorstand"
        Case 2
            GetSlideContent =   "1. mod_010_laden_reinigen.py" & vbCrLf & _
                                "mod_020_csv_analyzer.py" & vbCrLf & _
                                "mod_021_csv_analyzer_gassensor_010.py" & vbCrLf & _
                                "mod_040_feature_engeneering.py" & vbCrLf & _
                                "mod_041_Umrechnung_wert_ppm_µgm3.py" & vbCrLf & _
                                "mod_042_Umrechnung_wert_ppm_ygm3.py" & vbCrLf & _
                                "mod_043_glaetten_der_sensorwerte.py" & vbCrLf & _
                                "mod_045_datenanalyse plotten.py" & vbCrLf & _
                                "mod_050_gui copy.py" & vbCrLf & _
                                "mod_050_gui.py" & vbCrLf & _
                                "mod_060_visualization.py" & vbCrLf & _
                                "mod_070_reporting.py" & vbCrLf & _
                                "mod_080_text_generieren.py" & vbCrLf & _
                                "mod_090_bild_generieren.py" & vbCrLf & _
                                "mod_100_upload_wordpress.py" & vbCrLf & _
                                "mod_110_auswertung_gesamt.py" & vbCrLf & _ 
                                "Authentizitäts-Score zu Beginn: M-Score: " & m & " | R-Score: " & r
        Case 3
            GetSlideContent = 
                        "Projekt- und Datenordner bestimmen:" & vbCrLf & _
            "Sucht den Ordner bearbeitet relativ zum Projektspeicherort." & vbCrLf & _
            "" & vbCrLf & _
            "Erste CSV-Datei finden:" & vbCrLf & _
            "Sucht die erste .csv-Datei im Ordner bearbeitet." & vbCrLf & _
            "" & vbCrLf & _
            "Headerzeile suchen:" & vbCrLf & _
            "Liest die Datei zeilenweise ein und sucht explizit nach der bekannten Headerzeile (Spaltenüberschriften). Überspringt Zeilen, die mit # beginnen." & vbCrLf & _
            "" & vbCrLf & _
            "Datenzeilen bereinigen:" & vbCrLf & _
            "" & vbCrLf & _
            "Ersetzt alle ; durch ,." & vbCrLf & _
            "Entfernt ' MESZ' und ' UTC' aus den Datenzeilen (ab Header)." & vbCrLf & _
            "" & vbCrLf & _
            "Daten in DataFrame laden:" & vbCrLf & _
            "Liest die bereinigten Zeilen direkt in ein pandas-DataFrame ein." & vbCrLf & _
            "" & vbCrLf & _
            "Datumsspalten konvertieren:" & vbCrLf & _
            "Wandelt die Spalten DateTime und GPS_DateTime (falls vorhanden) in Datetime-Objekte um." & vbCrLf & _
            "" & vbCrLf & _
            "Erste X Minuten filtern:" & vbCrLf & _
            "Filtert alle Zeilen heraus, deren DateTime-Wert innerhalb der ersten X Minuten (aus der Konfiguration) liegt." & vbCrLf & _
            "" & vbCrLf & _
            "Zeilen ohne GPS-Daten entfernen:" & vbCrLf & _
            "Entfernt Zeilen, in denen GPS_Lat, GPS_Lon oder GPS_Alt leer, '--', 'nan' oder 'NaN' sind." & vbCrLf & _
            "" & vbCrLf & _
            "GPS_Course-Korrektur:" & vbCrLf & _
            "Setzt Werte in der Spalte GPS_Course auf 0, wenn sie mehr als 3 Ziffern haben." & vbCrLf & _
            "" & vbCrLf & _
            "Zeilen mit GPS_Lon < 8 entfernen:" & vbCrLf & _
            "Entfernt alle Zeilen, bei denen der Wert in GPS_Lon kleiner als 8 ist." & vbCrLf & _
            "" & vbCrLf & _
            "Letzte Zeile entfernen:" & vbCrLf & _
            "Entfernt die letzte Zeile des DataFrames (z.B. fehlerhafte Messung am Dateiende)." & vbCrLf & _
            "" & vbCrLf & _
            "Zielordner und Dateinamen bestimmen:" & vbCrLf & _
            "Legt den Zielordner bearbeitet0 an und bestimmt einen neuen Dateinamen anhand eines Zeitstempels im alten Dateinamen." & vbCrLf & _
            "" & vbCrLf & _
            "DataFrame als CSV speichern:" & vbCrLf & _
            "Speichert das bereinigte DataFrame als neue CSV-Datei im Zielordner." & vbCrLf & _
            "" & vbCrLf & _
            "Anzeigeoptionen setzen:" & vbCrLf & _
            "Setzt pandas-Optionen für eine bessere Anzeige im Terminal." & vbCrLf & _
            "" & vbCrLf & _
            "DataFrame zurückgeben:" & vbCrLf & _
            "Gibt das bereinigte DataFrame zurück." & vbCrLf & _
            "" & vbCrLf & _
            "(Optional, wenn als Skript ausgeführt):" & vbCrLf & _
            "" & vbCrLf & _
            "Gibt Spaltennamen und die ersten Zeilen aus." & vbCrLf & _
            "Zeigt transponierte Statistik." & vbCrLf & _
            "Erstellt Histogramme für numerische Spalten (ohne Anzeige)." & vbCrLf & _
            "Gibt „Fertig!“ aus." & vbCrLf & _
            
                            "- Datum_Tabelle (Kalenderhilfe)"
        Case 4
            GetSlideContent = "Unsere forensische Methodik:" & vbCrLf & _
                              "- Datenaufbereitung & Integritätsprüfung" & vbCrLf & _
                              "- Plausibilitäts-Checks (Geschäftslogik)" & vbCrLf & _
                              "- Abgleich mit internen Systemen" & vbCrLf & _
                              "- Mustererkennung (Hinweise auf künstliche Generierung)"
        Case 5
            GetSlideContent = "Beweis A: Datenintegrität" & vbCrLf & _
                              "Fakt 1: Kreditkartendaten & CVV im Klartext gespeichert" & vbCrLf & _
                              "Fakt 2: Logische Werte als Text ('YES' / 'NO') gespeichert" & vbCrLf & _
                              "Konsequenz: So speichert kein reales System – Verstoß gegen PCI-DSS" & vbCrLf & vbCrLf & _
                              "Score jetzt: M-Score " & m & ", R-Score " & r
        Case 6
            GetSlideContent = "Beweis B: Zeitmuster" & vbCrLf & _
                              "Analyse der Zeitstempel: Fast alle Transaktionen zwischen 08–20 Uhr CST" & vbCrLf & _
                              "Lücke zwischen 22–03 Uhr – kein globaler Fraud folgt diesem Muster" & vbCrLf & _
                              "Hinweis auf künstliche Generierung durch ein Skript" & vbCrLf & vbCrLf & _
                              "Score jetzt: M-Score " & m & ", R-Score " & r
        Case 7
            GetSlideContent = "Beweis C: Geschäftslogik & Verhalten" & vbCrLf & _
                              "Anomalie 1: Betrugsrate bei nur 0,17%" & vbCrLf & _
                              "Anomalie 2: Felder wie 'Renteneintrittsalter' unlogisch" & vbCrLf & _
                              "Anomalie 3: Negative Beträge ohne Storno-Markierung" & vbCrLf & vbCrLf & _
                              "Score jetzt: M-Score " & m & ", R-Score " & r
        Case 8
            GetSlideContent = "Beweis D: Datenmodell" & vbCrLf & _
                              "Problem 1: Keine Normalisierung – Tabellenbeziehungen fehlen" & vbCrLf & _
                              "Problem 2: 6.146 Karten mit abgelaufenem Datum aktiv genutzt" & vbCrLf & _
                              "Fazit: Kein professionelles relationales Modell" & vbCrLf & vbCrLf & _
                              "Score jetzt: M-Score " & m & ", R-Score " & r
        Case 9
            GetSlideContent = "Fallstudie: Der Versuch" & vbCrLf & _
                              "Experiment: Aufbau eines einfachen Fraud-Modells mit Power BI" & vbCrLf & _
                              "Kriterien: REDFLAG = TRUE, Fehler > 0, Betrag > 5000€, Swipe-Nutzung"
        Case 10
            GetSlideContent = "Fallstudie: Die Erkenntnis" & vbCrLf & _
                              "Das Modell war extrem treffsicher – zu gut" & vbCrLf & _
                              "Grund: Künstliche Muster in den Daten (z.B. Uhrzeit)" & vbCrLf & _
                              "Codebeispiel: Zeitregel (22–06 Uhr) schließt viele Transaktionen aus"
        Case 11
            GetSlideContent = "Fallstudie: Das Urteil" & vbCrLf & _
                              "Modell funktioniert – aber nur wegen künstlicher Muster" & vbCrLf & _
                              "Ergebnis: Daten unbrauchbar für echte Analyse" & vbCrLf & _
                              "Trainiert auf Fälschung, nicht Realität"
        Case 12
            GetSlideContent = "Beweiskette zusammengefasst:" & vbCrLf & _
                              "- Klartextdaten, Text statt Boolean" & vbCrLf & _
                              "- Zeitmuster widersprechen Realität" & vbCrLf & _
                              "- Strukturfehler im Modell" & vbCrLf & _
                              "- Unlogisches Kundenverhalten" & vbCrLf & vbCrLf & _
                              "Final Score: M-Score " & m & ", R-Score " & r
        Case 13
            GetSlideContent = "Empfehlung:" & vbCrLf & _
                              "- Keine reale Gefahr durch diesen Datensatz" & vbCrLf & _
                              "- Keine Zahlung / Kontakt zum Erpresser" & vbCrLf & _
                              "- Weiterleitung an Rechts & Kommunikation" & vbCrLf & _
                              "- (Optional) Prozessprüfung"
        Case 14
            GetSlideContent = "Vielen Dank für Ihre Aufmerksamkeit." & vbCrLf & _
                              "Gerne beantworte ich Ihre Fragen."
        Case 15
            GetSlideContent = "Anhang A1 – Datenaufbereitung:" & vbCrLf & _
                              "- Rohdaten extrahiert" & vbCrLf & _
                              "- Bereinigung, Typ-Korrektur, Duplikate, Geodaten"
        Case 16
            GetSlideContent = "Anhang A1 – Modellaufbau:" & vbCrLf & _
                              "- Sternschema: Verknüpfung users/cards/mcc/time" & vbCrLf & _
                              "- CALENDARAUTO, berechnete Spalten"
        Case 17
            GetSlideContent = "Anhang A2 – Analytische Fragen:" & vbCrLf & _
                              "- Karten je Kunde?" & vbCrLf & _
                              "- Transaktionen nach Alter?" & vbCrLf & _
                              "- Einkommen vs FICO? Schulden vs Limit?"
        Case 18
            GetSlideContent = "Anhang A2 – Reporting in Power BI:" & vbCrLf & _
                              "- Übersicht ? Betrugs-Detail ? Kunden-Profil" & vbCrLf & _
                              "- Filter, Drillthrough, Tabs für Betrug/Kunde/Trends"
    End Select
End Function


Function GetSlideNotes(idx As Long) As String
    ' (Code wie von Ihnen bereitgestellt)
    Select Case idx
        Case 1: GetSlideNotes = "Kontext, Ziel und Datensatz vom 05.06.2025 – 'wir präsentieren Fakten, keine Meinung.'"
        Case 2: GetSlideNotes = "Agenda vorstellen, Kernaussage direkt unten platzieren. Score-Logik erklären."
        Case 3: GetSlideNotes = "Neutral beschreiben, um Spannung aufzubauen."
        Case 4: GetSlideNotes = "Prozess fachlich darstellen – Flussdiagramm visuell planen."
        Case 5: GetSlideNotes = "Highlight: Klartext-CVV – PCI-Compliance, 'Red Flag'."
        Case 6: GetSlideNotes = "Grafik zeigt Lücke 22–03 Uhr – typisches Skript-Muster."
        Case 7: GetSlideNotes = "Unlogische Felder & Betrugsrate anteasern."
        Case 8: GetSlideNotes = "Datenmodell chaotisch = kein echtes System."
        Case 9: GetSlideNotes = "Modell erzeugt – 'sehen Sie, was passiert, wenn wir mit den Daten arbeiten'."
        Case 10: GetSlideNotes = "Zeitregel-Code zeigt Daten-Generator-Signatur."
        Case 11: GetSlideNotes = "Datensatz unbrauchbar – Zusammenführen mit vorherigen Scores."
        Case 12: GetSlideNotes = "Score 15:0 – klares visuelles Statement."
        Case 13: GetSlideNotes = "Souveräne Empfehlung – Prozess & Kommunikation."
        Case 14: GetSlideNotes = "Ruhiger Call-to-Action: Fragen stellen."
        Case 15: GetSlideNotes = "Detail: Von Rohdaten bis Typen-Bereinigung"
        Case 16: GetSlideNotes = "Detail: Modellstruktur & Zeitintelligenz"
        Case 17: GetSlideNotes = "Echte Fragestellungen für reale Daten"
        Case 18: GetSlideNotes = "Power BI Konzept: interaktive Tabs & Filter"
    End Select
End Function

