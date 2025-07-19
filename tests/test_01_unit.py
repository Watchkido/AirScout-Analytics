"""
test_01_unit.py
Unittests für einzelne Funktionen.
Hier werden Funktionseinheiten getestet.
"""

def test_addiere():
    from src.Projekt_Generator.utils.helper import addiere
    assert addiere(2, 3) == 5
