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

