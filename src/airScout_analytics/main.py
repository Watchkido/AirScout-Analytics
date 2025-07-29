import os
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=Warning)

# Kontext robust importieren (funktioniert bei Direktstart und Modulstart)
try:
    import context as context
except ImportError:
    from . import context

def main():
    """
    Startet die Pipeline, indem das Hauptskript importiert und ausführt wird.
    """
    try:
        # warnings explizit im Funktionsscope verfügbar machen
        global warnings
        try:
            import mod_000_pipeline
        except ImportError:
            from . import mod_000_pipeline
        if hasattr(mod_000_pipeline, 'main'):
            mod_000_pipeline.main()
        else:
            print("mod_000_pipeline hat keine main()-Funktion, führe als Skript aus...")
            pfad = os.path.join(os.path.dirname(__file__), 'mod_000_pipeline.py')
            with open(pfad, encoding='utf-8') as f:
                exec(f.read(), globals())
    except Exception as e:
        print(f"Fehler beim Starten der Pipeline: {e}")

if __name__ == "__main__":
    main()