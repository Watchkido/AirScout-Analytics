@echo off
REM 📊 SCHNELLSTART FÜR GASSENSOR-ANALYSE
echo 🚀 GASSENSOR CSV ANALYZER - SCHNELLSTART
echo ==========================================

REM Prüfen ob Python-Umgebung vorhanden ist
if not exist ".venv\Scripts\python.exe" (
    echo ❌ Python-Umgebung nicht gefunden!
    echo    Führe zuerst die Ersteinrichtung durch:
    echo    python -m venv .venv
    echo    .venv\Scripts\activate
    echo    pip install pandas scikit-learn scipy matplotlib seaborn
    pause
    exit /b 1
)

REM Skript ausführen
echo 🔍 Starte Gassensor-Analyse...
.venv\Scripts\python.exe csv_analyzer_gassensor_fixed.py %1

echo.
echo ✅ Analyse abgeschlossen!
echo 📂 Überprüfe die erstellten _info.txt und _info.csv Dateien
pause
