import os
import ast

def finde_und_liste_alle_funktionen(verzeichnis: str = ".") -> None:
    """
    Listet alle Funktionen in allen Python-Dateien des Projekts auf.
    :param verzeichnis: Startverzeichnis (Standard: aktuelles Verzeichnis)
    """
    ergebnis_datei = os.path.join(os.path.dirname(__file__), "..", "..", "import_analyse_ergebnis.txt")
    with open(ergebnis_datei, "a", encoding="utf-8") as ergebnis:
        for root, _, files in os.walk(verzeichnis):
            for file in files:
                if file.endswith(".py") and not file.startswith("test_"):
                    pfad = os.path.join(root, file)
                    rel_pfad = os.path.relpath(pfad, verzeichnis)
                    try:
                        with open(pfad, "r", encoding="utf-8") as f:
                            inhalt = f.read()
                        baum = ast.parse(inhalt)
                        funktionen = [
                            node.name for node in ast.walk(baum)
                            if isinstance(node, ast.FunctionDef)
                        ]
                        if funktionen:
                            print(f"\nFunktionen in {rel_pfad}:")
                            ergebnis.write(f"\nFunktionen in {rel_pfad}:\n")
                            for name in funktionen:
                                print(f"  - {name}()")
                                ergebnis.write(f"  - {name}()\n")
                    except Exception as e:
                        print(f"Fehler beim Verarbeiten von {rel_pfad}: {e}")

if __name__ == "__main__":
    finde_und_liste_alle_funktionen()

