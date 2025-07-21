"""
modul1.py
Beispiel-Modul 1.
Hier können Funktionen oder Klassen für Modul 1 implementiert werden.
"""
from config import CONFIG
# pipeline.py

import config
import 010_daten_laden as laden
import 020_daten_reinigen as reinigen
import 030_feature_engineering as featurize
import 040_datenanalyse_plotten as plotten
import 050_text_generieren as texten
import 060_bild_generieren as bilder
import 070_upload_wordpress as upload
import dashboard_gui

def main():
    df = laden.lade_daten(config.DATEN_PFAD)
    df = reinigen.reinige_daten(df)
    df = featurize.berechne_merkmale(df)
    plotten.erstelle_plots(df)
    texte = texten.generiere_text(df)
    bildpfade = bilder.generiere_bilder(df)
    upload.upload(texte, bildpfade)
    dashboard_gui.zeige_dashboard()

if __name__ == "__main__":
    main()

    pass