import os
from Projekt_Generator.config import CONFIG
from Projekt_Generator.template_tools import copy_template

def kopfkommentar(dateiname, beschreibung, inhalt):
    return f'"""\n{dateiname}\n{beschreibung}\n{inhalt}\n"""\n\n'

def erstelle_struktur(projekt, nutzer, privat, basis_pfad=None):
    """
    Erstellt die Projektstruktur mit kleingeschriebenem Projektordner und
    Quellcode-Ordner in PascalCase.

    :param projekt: Projektname (beliebig)
    :param nutzer: Nutzername
    :param privat: Privat-Flag
    :param basis_pfad: Optionaler Basis-Pfad
    """
    if basis_pfad is None:
        basis_pfad = CONFIG.PROJEKT_PFAD

    projekt_ordner = projekt.lower()
    quellcode_ordner = projekt[:1].upper() + projekt[1:]  # PascalCase (einfach)
    projekt_pfad = os.path.join(basis_pfad, projekt_ordner)

    struktur = [                                        
        f"{projekt_pfad}/src/{quellcode_ordner}",
        f"{projekt_pfad}/src/{quellcode_ordner}/utils",
        f"{projekt_pfad}/tests",
        f"{projekt_pfad}/prompts",
        f"{projekt_pfad}/scripts",
        f"{projekt_pfad}/data/raw",
        f"{projekt_pfad}/data/processed",
        f"{projekt_pfad}/data/results",
        f"{projekt_pfad}/data/merged",
        f"{projekt_pfad}/data/finished",
        f"{projekt_pfad}/data/cached",
        f"{projekt_pfad}/docs",
        f"{projekt_pfad}/datenbank",
        f"{projekt_pfad}/notebooks",
    ]

    files = {
        "README.md": f"{projekt_pfad}\\README.md",
        ".gitignore": f"{projekt_pfad}\\.gitignore",
        "requirements.txt": f"{projekt_pfad}\\requirements.txt",
        "requirements-dev.txt": f"{projekt_pfad}\\requirements-dev.txt",
        "LICENSE": f"{projekt_pfad}\\LICENSE",
        "agent.md": f"{projekt_pfad}\\agent.md",
        "claude.md": f"{projekt_pfad}\\claude.md",
        "copilot_instruction.md": f"{projekt_pfad}\\copilot_instruction.md",
        "coursroles.md": f"{projekt_pfad}\\coursroles.md",
        "pyproject.toml": f"{projekt_pfad}\\pyproject.toml",
        ".copilot\\config.json": f"{projekt_pfad}\\.copilot\\config.json",
        ".copilot\\README.md": f"{projekt_pfad}\\.copilot\\README.md",  




        "src\\__init__.py": f"{projekt_pfad}\\src\\{quellcode_ordner}\\__init__.py",
        "src\\data_loader.py": f"{projekt_pfad}\\src\\{quellcode_ordner}\\data_loader.py",    
        "src\\feature_engineering.py": f"{projekt_pfad}\\src\\{quellcode_ordner}\\feature_engineering.py",
        "src\\outlier_detection.py": f"{projekt_pfad}\\src\\{quellcode_ordner}\\outlier_detection.py",
        "src\\data_visualization.py": f"{projekt_pfad}\\src\\{quellcode_ordner}\\data_visualization.py",
        "src\\modeling_pipeline.py": f"{projekt_pfad}\\src\\{quellcode_ordner}\\modeling_pipeline.py",
        "src\\model_evaluation.py": f"{projekt_pfad}\\src\\{quellcode_ordner}\\model_evaluation.py",
        "src\\reporting.py": f"{projekt_pfad}\\src\\{quellcode_ordner}\\reporting.py",
        "src\\preprocessing.py": f"{projekt_pfad}\\src\\{quellcode_ordner}\\preprocessing.py",
        "src\\analysis.py": f"{projekt_pfad}\\src\\{quellcode_ordner}\\analysis.py",
        "src\\visualization.py": f"{projekt_pfad}\\src\\{quellcode_ordner}\\visualization.py",
        "src\\main.py": f"{projekt_pfad}\\src\\{quellcode_ordner}\\main.py",
        "src\\projekt_analyse.py": f"{projekt_pfad}\\src\\{quellcode_ordner}\\projekt_analyse.py",
        "src\\config.py": f"{projekt_pfad}\\src\\{quellcode_ordner}\\config.py",
        "src\\constants.py": f"{projekt_pfad}\\src\\{quellcode_ordner}\\constants.py",
        "src\\logging_config.py": f"{projekt_pfad}\\src\\{quellcode_ordner}\\logging_config.py",
        "src\\exceptions.py": f"{projekt_pfad}\\src\\{quellcode_ordner}\\exceptions.py",
        "src\\modul1.py": f"{projekt_pfad}\\src\\{quellcode_ordner}\\modul1.py",
        "src\\modul2.py": f"{projekt_pfad}\\src\\{quellcode_ordner}\\modul2.py",
        "src\\gui.py": f"{projekt_pfad}\\src\\{quellcode_ordner}\\gui.py",
        "src\\main_gui.py": f"{projekt_pfad}\\src\\{quellcode_ordner}\\main_gui.py",    
        "src\\spracheingabe.py": f"{projekt_pfad}\\src\\{quellcode_ordner}\\spracheingabe.py",
        "src\\funktionen.py": f"{projekt_pfad}\\src\\{quellcode_ordner}\\funktionen.py",

        "src\\datenbank.py": f"{projekt_pfad}\\src\\{quellcode_ordner}\\datenbank.py",
        "src\\datenbank\\__init__.py": f"{projekt_pfad}\\src\\{quellcode_ordner}\\datenbank\\__init__.py",
        "src\\datenbank\\db_connection.py": f"{projekt_pfad}\\src\\ {quellcode_ordner}\\datenbank\\db_connection.py",
        "src\\datenbank\\db_queries.py": f"{projekt_pfad}\\src\\{quellcode_ordner}\\datenbank\\db_queries.py",
        "src\\datenbank\\db_utils.py": f"{projekt_pfad}\\src\\{quellcode_ordner}\\datenbank\\db_utils.py",
  
        "src\\utils\\__init__.py": f"{projekt_pfad}\\src\\{quellcode_ordner}\\utils\\__init__.py",
        "src\\utils\\helper.py": f"{projekt_pfad}\\src\\{quellcode_ordner}\\utils\\helper.py",
        "src\\utils\\konstanten.py": f"{projekt_pfad}\\src\\{quellcode_ordner}\\utils\\konstanten.py",
        "src\\utils\\projekt_anlyse.py": f"{projekt_pfad}\\src\\{quellcode_ordner}\\utils\\projekt_analyse.py",

        "tests\\test_01_unit.py": f"{projekt_pfad}\\tests\\test_01_unit.py",
        "tests\\test_02_integration.py": f"{projekt_pfad}\\tests\\test_02_integration.py",
        "tests\\test_03_system.py": f"{projekt_pfad}\\tests\\test_03_system.py",
        "tests\\test_04_fuzz.py": f"{projekt_pfad}\\tests\\test_04_fuzz.py",
        "tests\\test_05_penetration.py": f"{projekt_pfad}\\tests\\test_05_penetration.py",
        "tests\\test_05_security.py": f"{projekt_pfad}\\tests\\test_05_security.py",
        "tests\\test_07_performance.py": f"{projekt_pfad}\\tests\\test_07_performance.py",
        "tests\\test_08_Affe.py": f"{projekt_pfad}\\tests\\test_08_Affe.py",
        "tests\\test_09_wiederherstellbarkeit.py": f"{projekt_pfad}\\tests\\test_09_wiederherstellbarkeit.py",
        "tests\\test_10_Umwelt.py": f"{projekt_pfad}\\tests\\test_10_Umwelt.py",
        "tests\\__init__.py": f"{projekt_pfad}\\tests\\__init__.py",

        "prompts\\prompt01.txt": f"{projekt_pfad}\\prompts\\prompt01.txt",
        "prompts\\prompt02.txt": f"{projekt_pfad}\\prompts\\prompt02.txt",
        "prompts\\prompt03.txt": f"{projekt_pfad}\\prompts\\prompt03.txt",

        "scripts\\template_00_data_processing.py": f"{projekt_pfad}\\scripts\\template_00_data_processing.py",
        "scripts\\template_01_data_loader.py": f"{projekt_pfad}\\scripts\\template_01_data_loader.py",
        "scripts\\template_02_data_exploration.py": f"{projekt_pfad}\\scripts\\template_02_data_exploration.py",
        "scripts\\template_03_data_cleanup.py": f"{projekt_pfad}\\scripts\\template_03_data_cleanup.py",
        "scripts\\template_04_feature_engineering.py": f"{projekt_pfad}\\scripts\\template_04_feature_engineering.py",
        "scripts\\template_05_data_imputation.py": f"{projekt_pfad}\\scripts\\template_05_data_imputation.py",
        "scripts\\template_06_outlier_detection.py": f"{projekt_pfad}\\scripts\\template_06_outlier_detection.py",
        "scripts\\template_07_data_visualization.py": f"{projekt_pfad}\\scripts\\template_07_data_visualization.py",
        "scripts\\template_08_modeling_pipeline.py": f"{projekt_pfad}\\scripts\\template_08_modeling_pipeline.py",
        "scripts\\template_09_model_evaluation.py": f"{projekt_pfad}\\scripts\\template_09_model_evaluation.py",
        "scripts\\template_10_reporting.py": f"{projekt_pfad}\\scripts\\template_10_reporting.py",

        "notebooks\\010_Installation.ipynb": f"{projekt_pfad}\\notebooks\\analysis.ipynb",
        "notebooks\\020_duplikate.ipynb":   f"{projekt_pfad}\\notebooks\\020_duplikate.ipynb",
        "notebooks\\030_Fehler .ipynb": f"{projekt_pfad}\\notebooks\\030_Analyse.ipynb", 
        "notebooks\\040_Analyse.ipynb": f"{projekt_pfad}\\notebooks\\040_Analyse.ipynb",
        "notebooks\\datentypen_pruefen.ipynb":   f"{projekt_pfad}\\notebooks\\datentypen_pruefen.ipynb", 
        "notebooks\\Encoding.ipynb":    f"{projekt_pfad}\\notebooks\\Encoding.ipynb",
        "notebooks\\features_engeneering.ipynb":    f"{projekt_pfad}\\notebooks\\features_engeneering.ipynb", 
        "notebooks\\binning.ipynb":     f"{projekt_pfad}\\notebooks\\binning.ipynb",
        "notebooks\\normalization.ipynb":   f"{projekt_pfad}\\notebooks\\normalization.ipynb",
        "notebooks\\korrelation.ipynb":     f"{projekt_pfad}\\notebooks\\korrelation.ipynb",
        "notebooks\\ersetzen.ipynb":    f"{projekt_pfad}\\notebooks\\ersetzen.ipynb",
        "notebooks\\loeschen.ipynb":    f"{projekt_pfad}\\notebooks\\loeschen.ipynb",
        "notebooks\\analysis.ipynb":    f"{projekt_pfad}\\notebooks\\analysis.ipynb",
        "notebooks\\grundlagen.ipynb":  f"{projekt_pfad}\\notebooks\\grundlagen.ipynb",
        "notebooks\\next_step.ipynb":   f"{projekt_pfad}\\notebooks\\next_step.ipynb",
        "notebooks\\sandbox.ipynb":     f"{projekt_pfad}\\notebooks\\sandbox.ipynb",
        "notebooks\\report.ipynb":     f"{projekt_pfad}\\notebooks\\report.ipynb",
        "notebooks\\strukturierte _daten.ipynb":    f"{projekt_pfad}\\notebooks\\strukturierte_daten.ipynb",
        "notebooks\\report.ipynb": f"{projekt_pfad}\\notebooks\\report.ipynb",
        



    }

    for folder in struktur:
        os.makedirs(folder, exist_ok=True)

    for template_name, target_path in files.items():
        template_path = os.path.join(CONFIG.TEMPLATE_DIR, template_name)
        replacements = {
            "{projekt}": projekt,
            "{nutzer}": nutzer,
        }
        try:
            copy_template(template_path, target_path, replacements)
        except Exception as e:
            print(f"Fehler beim Kopieren von {template_path} nach {target_path}: {e}")