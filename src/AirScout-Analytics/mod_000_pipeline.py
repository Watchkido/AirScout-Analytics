"""
modul1.py
Beispiel-Modul 1.
Hier können Funktionen oder Klassen für Modul 1 implementiert werden.
"""


from config import CONFIG
from mod_010_laden_reinigen import laden_und_reinigen

def main():
    df = laden_und_reinigen()
    # Hier können weitere Pipeline-Schritte ergänzt werden
    print('Pipeline erfolgreich ausgeführt.')

if __name__ == "__main__":
    main()