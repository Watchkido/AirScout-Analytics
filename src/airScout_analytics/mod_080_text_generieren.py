"""
006_Umweltkontrollsystem  watchkido
preprocessing.py
Funktionen zur Datenbereinigung und Vorverarbeitung.
Hier werden Funktionen zur Bereinigung, Transformation und Vorbereitung der Daten definiert.
"""
from config import CONFIG

# Für .env-Handling und HTTP-Requests
import os
import requests
from typing import Optional

# Für Google Gemini SDK
import google.generativeai as genai

def lade_gemini_api_key(env_pfad: str = ".env") -> Optional[str]:
    """
    Liest den Gemini API-Key aus einer .env-Datei im Hauptverzeichnis.
    :param env_pfad: Pfad zur .env-Datei
    :return: API-Key als String oder None
    """
    if not os.path.exists(env_pfad):
        print(f".env-Datei nicht gefunden: {env_pfad}")
        return None
    with open(env_pfad, encoding="utf-8") as f:
        for line in f:
            if line.strip().startswith("GEMINI_API_KEY"):
                return line.strip().split("=", 1)[-1].strip()
    print("GEMINI_API_KEY nicht in .env gefunden.")
    return None

def generiere_luftqualitaetsbericht_von_gemini(prompt_txt_pfad: str) -> str:
    """
    Holt einen Luftqualitätsbericht für Neustadt an der Weinstraße von Gemini.
    Der Prompt wird aus einer TXT-Datei geladen. Der API-Key wird aus .env gelesen.

    :param prompt_txt_pfad: Pfad zur TXT-Datei mit dem Prompt
    :return: Generierter Bericht als String (oder Fehlermeldung)
    """
    api_key = lade_gemini_api_key(os.path.join(os.path.dirname(__file__), '../../.env'))
    if not api_key:
        return "[Fehler] Kein Gemini API-Key gefunden."
    if not os.path.exists(prompt_txt_pfad):
        return f"[Fehler] Prompt-Datei nicht gefunden: {prompt_txt_pfad}"
    with open(prompt_txt_pfad, encoding="utf-8") as f:
        prompt_text = f.read()

    try:
        genai.configure(api_key=api_key)
        # Modellname kann angepasst werden (z.B. "gemini-2.5-flash" oder "gemini-1.5-pro-latest")
        model_name = "gemini-2.5-flash"
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt_text)
        return response.text
    except Exception as e:
        return f"[Fehler] Anfrage an Gemini SDK fehlgeschlagen: {e}"

# module/050_text_generieren.py

def generiere_text(df):
    """
    Erstellt einen einfachen Umweltbericht aus dem letzten DataFrame-Eintrag.
    :param df: DataFrame mit Umweltdaten
    :return: Liste mit Berichtstext
    """
    letzte = df.iloc[-1]
    text = (
        f"📅 Umweltbericht am {letzte['DateTime']}:\n"
        f"🌡 Temperatur: {letzte['Temperature_DHT_C']}°C\n"
        f"💧 Luftfeuchtigkeit: {letzte['Humidity_RH']}%\n"
        f"🔥 CO-Konzentration: {letzte['MQ7']} ppm\n"
    )
    if letzte.get('CO_Warnung', False):
        text += "⚠️ Warnung: Kritischer CO-Wert erkannt!"
    return [text]



# === Pipeline-kompatibler Einstiegspunkt ===
def main():
    """
    Pipeline-kompatibler Einstiegspunkt: Holt Umweltbericht von Gemini und speichert ihn im Ergebnisordner.
    """
    # Kontext importieren
    import sys
    import importlib
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    context = importlib.import_module('airScout_analytics.context')
    filename_ohne_ext = getattr(context, 'filename_ohne_ext', None)
    if not filename_ohne_ext:
        print("[Fehler] context.filename_ohne_ext ist nicht gesetzt!")
        return False
    # Absoluter Pfad zum Projekt-Hauptverzeichnis
    projekt_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
    ergebnisse_dir = os.path.join(projekt_root, 'data', 'ergebnisse', filename_ohne_ext)
    prompt_pfad = os.path.join(ergebnisse_dir, f"{filename_ohne_ext}_info.txt")
    ausgabe_pfad = os.path.join(ergebnisse_dir, "umweltbericht.txt")
    os.makedirs(ergebnisse_dir, exist_ok=True)
    bericht = generiere_luftqualitaetsbericht_von_gemini(prompt_pfad)
    with open(ausgabe_pfad, "w", encoding="utf-8") as f:
        f.write(bericht)
    print(f"✅ Umweltbericht gespeichert unter: {ausgabe_pfad}")
    return True

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Fehler bei der Textgenerierung: {e}")


