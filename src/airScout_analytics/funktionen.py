import os
import subprocess
import sys
from Projekt_Generator.projektstruktur import erstelle_struktur
from Projekt_Generator.git_tools import initialisiere_git_und_push
from Projekt_Generator.skript_tools import finde_scripts, run_python_script

def projekt_anlegen(projekt: str, nutzer: str, privat: bool, basis_pfad: str) -> str:
    """
    Legt ein neues Projekt an und initialisiert ein Git-Repository.
    Gibt eine Statusmeldung zurück.
    """
    pfad = os.path.join(basis_pfad, projekt)
    if os.path.exists(pfad):
        return "Ordner existiert bereits."
    erstelle_struktur(projekt, nutzer, privat, basis_pfad)
    initialisiere_git_und_push(projekt, nutzer, privat, basis_pfad)
    return f"Projekt '{projekt}' wurde erfolgreich erstellt!"

def skript_ausführen(skript_pfad: str):
    """
    Führt ein Python-Skript aus und gibt (stdout, stderr, fehler) zurück.
    """
    return run_python_script(skript_pfad)

def projekt_analyse_starten():
    """
    Startet das Analyse-Skript im utils-Ordner.
    """
    skript_pfad = os.path.join(os.path.dirname(__file__), "utils", "projekt_analyse.py")
    subprocess.Popen([sys.executable, skript_pfad])

def finde_alle_scripts():
    """
    Gibt ein Dictionary aller gefundenen Skripte zurück.
    """
    return finde_scripts()
