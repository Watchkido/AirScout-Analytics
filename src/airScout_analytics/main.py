
import os
import sys
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=Warning)
# main.py
import airScout_analytics.context as context
context.filename = generate_filename_based_on_date()



# Startet die Pipeline, indem das Hauptskript importiert und ausgeführt wird
def main():
    try:
        import mod_000_pipeline
        if hasattr(mod_000_pipeline, 'main'):
            mod_000_pipeline.main()
        else:
            print("mod_000_pipeline hat keine main()-Funktion, führe als Skript aus...")
            # Fallback: führe das Skript direkt aus
            exec(open(os.path.join(os.path.dirname(__file__), 'mod_000_pipeline.py'), encoding='utf-8').read(), globals())
    except Exception as e:
        print(f"Fehler beim Starten der Pipeline: {e}")





#  führt das Skript aus
if __name__ == "__main__":
    main()
# python -m csv_analyser.main