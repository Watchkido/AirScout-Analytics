import os
import subprocess
from projektstruktur import erstelle_struktur
from git_tools import initialisiere_git_und_push
from skript_tools import finde_scripts, run_python_script
import sys
from config import CONFIG

# module/070_upload_wordpress.py

import requests
from requests.auth import HTTPBasicAuth
import config

def upload(texts, images):
    for text, img in zip(texts, images):
        with open(img, 'rb') as f:
            medien_antwort = requests.post(
                "https://watchkido.de/wp-json/wp/v2/media",
                headers={'Content-Disposition': f'attachment; filename="{img}"'},
                files={'file': f},
                auth=HTTPBasicAuth(config.WP_BENUTZERNAME, config.WP_PASSWORT)
            )
        bild_id = medien_antwort.json().get('id')

        beitrag = {
            'title': 'Automatischer Umweltbericht',
            'content': text,
            'status': 'publish',
            'featured_media': bild_id
        }

        response = requests.post(
            config.WP_API_URL,
            json=beitrag,
            auth=HTTPBasicAuth(config.WP_BENUTZERNAME, config.WP_PASSWORT)
        )
        print("Beitrag veröffentlicht:", response.status_code)

def main() -> bool:
    """
    Pipeline-kompatibler Einstiegspunkt: Sucht Texte und Bilder im Ergebnisordner und lädt sie zu WordPress hoch.
    """
    import importlib
    import glob
    import os
    # Kontext laden
    context = importlib.import_module('airScout_analytics.context')
    filename_ohne_ext = getattr(context, 'filename_ohne_ext', None)
    if not filename_ohne_ext:
        print("[Fehler] context.filename_ohne_ext ist nicht gesetzt!")
        return False
    ergebnisse_dir = os.path.join("data", "ergebnisse", filename_ohne_ext)
    # Suche nach Texten und Bildern
    text_dateien = glob.glob(os.path.join(ergebnisse_dir, "*.txt"))
    bild_dateien = glob.glob(os.path.join(ergebnisse_dir, "*.png"))
    if not text_dateien or not bild_dateien:
        print("[Fehler] Keine Text- oder Bilddateien im Ergebnisordner gefunden.")
        return False
    # Texte laden
    texte = []
    for pfad in text_dateien:
        with open(pfad, encoding="utf-8") as f:
            texte.append(f.read())
    # Upload durchführen
    upload(texte, bild_dateien)
    print(f"✅ Upload zu WordPress abgeschlossen für {len(texte)} Texte und {len(bild_dateien)} Bilder.")
    return True


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Fehler beim WordPress-Upload: {e}")

