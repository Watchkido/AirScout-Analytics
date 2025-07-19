"""
exceptions.py
Benutzerdefinierte Ausnahmen für das Projekt.
Hier werden eigene Exception-Klassen definiert.
"""
from config import CONFIG
class CustomError(Exception):
    pass

class ValidationError(CustomError):
    pass
        
if __name__ == "__main__":
    # Code hier drunter wird nur ausgeführt wenn das Skript direkt aufgerufen wird
    pass