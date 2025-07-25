
import unittest
import sys
import os

class TestMainPipeline(unittest.TestCase):
    def test_pipeline_runs_without_exception(self):
        """
        Testet, ob main() ohne Exception durchläuft.
        Erwartet keine Rückgabe, prüft nur auf Fehlerfreiheit.
        """
        # Füge src/airScout_analytics zum sys.path hinzu (nach Umbenennung!)
        modulpfad = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/airScout_analytics'))
        if modulpfad not in sys.path:
            sys.path.insert(0, modulpfad)
        try:
            import main
            main.main()
        except Exception as e:
            self.fail(f"main() löste eine Exception aus: {e}")


if __name__ == "__main__":
    unittest.main()


