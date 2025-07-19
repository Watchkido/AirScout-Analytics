"""
config.py    print(CONFIG.BASIS_PFAD)
Konfigurationseinstellungen für das Projekt.
Hier werden globale Einstellungen und Parameter definiert.
"""
import datetime
from types import SimpleNamespace

def aktuelle_version():
    """Gibt einen Zeitstempel für die aktuelle Version zurück."""
    return datetime.datetime.now().strftime("%Y-%m-%d--%H:%M:%SMESZ")

CONFIG = SimpleNamespace(
    BASIS_PFAD = r"E:\dev\projekt_python_venv",
    PROJEKT_PFAD = r"E:\dev\projekt_python_venv\AirScout-Analytics",
    PROJEKT_NAME = "AirScout-Analytics",
    PROJEKT_BESCHREIBUNG = "Ein generisches Projekt, das als Vorlage für neue Python-Projekte dient.",
    PROJEKT_TYP = "Python-Projekt",
    PROJEKT_KATEGORIE = "Softwareentwicklung",
    PROJEKT_SCHLAGWORTE = ["Python", "Vorlage", "Projekt", "Generator"],
    PROJEKT_ZIELGRUPPE = "Entwickler, die eine Vorlage für neue Python-Projekte suchen",
    EMAIL = f"script-{aktuelle_version()}@watchkido.de",
    AUTOR = "Frank Albrecht",
    VERSION = aktuelle_version(),
    LIZENZ = "MIT License",
    GITHUB_USER = "watchkido",
    ORDNER_STRUKTUR = [
        "src/AirScout-Analytics",
        "src/AirScout-Analytics/utils",
        "tests",
        "prompts"
        "scripts",
        "data/raw",
        "data/processed",
        "notebooks",
    ],
    REQUIREMENTS = "requirements.txt",
    DEBUG = False,
    LOG_LEVEL =  "INFO",
    DEFAULT_ENCODING = "utf-8",
    SPRACHE = "de"
    
    
)