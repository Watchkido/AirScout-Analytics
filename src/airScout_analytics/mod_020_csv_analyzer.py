import os
import glob
import sys
import re
import warnings
import numpy as np
import pandas as pd
from datetime import datetime
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import SelectKBest, f_regression, mutual_info_regression
from scipy import stats
from config import CONFIG

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=Warning)


def main() -> str | None:
    """
    Pipeline-kompatibler Einstiegspunkt: Führt csv_info_extractor für die erste Datei in data/bearbeitet0 aus.
    Gibt den Pfad zur Info-Textdatei zurück oder None bei Fehler.
    """
    csv_ordner = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "data", "bearbeitet0"
    )
    csv_files = glob.glob(os.path.join(csv_ordner, "*.csv"))
    if not csv_files:
        print(f"Keine CSV-Datei in {csv_ordner} gefunden!")
        return None
    return csv_info_extractor(csv_files[0])



# 📊 CSV ANALYSE UND INFO-EXPORT SCRIPT MIT ERWEITERTEN ANALYTICS
'''
mod_020_csv_analyzer.py
=======================
Dieses Modul bietet ein umfassendes Analyse- und Informations-Export-Skript
für CSV-Dateien mit Sensordaten, insbesondere für Projekte im Bereich
AirScout Analytics. Es kombiniert klassische Datenanalyse mit erweiterten
Machine-Learning-Techniken zur Untersuchung von Sensorwerten (z.B.
MQ-Gassensoren).

Hauptfunktionen:
----------------
- **csv_info_extractor**: Robust geladenes Einlesen von CSV-Dateien mit
  automatischer Trennzeichenerkennung, Erzeugung eines ausführlichen
  Analyse-Reports als TXT-Datei. Der Report enthält u.a.:
    - Grundlegende Informationen (Shape, Dateigröße, Datentypen)
    - Beispielwerte pro Spalte
    - Head/Tail der Daten
    - Nullwert-Analyse mit Beispielen
    - Statistiken für numerische und kategoriale Spalten
    - Korrelationen und Duplikate
    - Erweiterte Analysen (Clustering, PCA, Zeitreihen, Feature Selection)
    - Zusammenfassung und Empfehlungen
- **erweiterte_sensor_analyse**: Führt verschiedene ML-Analysen auf
  Sensordaten durch:
    - Clustering von MQ-Sensoren (KMeans)
    - Hauptkomponentenanalyse (PCA)
    - Zeitreihenanalyse (Trends, Variabilität)
    - Auswahl unabhängiger Sensoren (Feature Selection)
- **mq_sensor_clustering**: Gruppiert MQ-Sensoren nach Ähnlichkeit ihres
  Verhaltens.
- **hauptkomponenten_analyse**: Reduziert die Dimensionalität der
  Sensordaten und identifiziert die wichtigsten Sensoren pro Komponente.
- **zeitreihen_veraenderungs_analyse**: Analysiert Trends und Variabilität
  der Sensorwerte über die Zeit.
- **unabhaengige_sensoren_waehlen**: Identifiziert und empfiehlt möglichst
  unabhängige Sensoren für weitere Analysen.

Besonderheiten:
---------------
- Automatische und robuste CSV-Parsing-Strategien (verschiedene
  Trennzeichen, Fehlerbehandlung)
- Speicherung der Analyseberichte an mehreren Zielorten mit Zeitstempel
- Umfangreiche Ausgaben für Debugging und Nachvollziehbarkeit
- Konfigurierbare Schwellenwerte und Analyseparameter über ein zentrales
  CONFIG-Objekt

Verwendung:
-----------
Das Skript kann direkt ausgeführt werden und sucht automatisch nach einer
CSV-Datei im Standardordner. Alternativ kann die Hauptfunktion für beliebige
CSV-Dateien aufgerufen werden.

Beispiel:
---------
    python mod_020_csv_analyzer.py <pfad/zur/datei.csv>

Abhängigkeiten:
---------------
- pandas, numpy, scikit-learn, scipy, matplotlib, seaborn
'''

warnings.filterwarnings('ignore')


def csv_info_extractor(csv_filepath):
    """
    Extrahiert alle wichtigen Informationen aus einer CSV-Datei
    und speichert sie in eine _info.txt-Datei
    """
    try:
        # CSV-Datei robuster laden mit verschiedenen Methoden
        df = None
        
        # Methode 1: Standard CSV-Laden (Komma-separiert)
        try:
            df = pd.read_csv(csv_filepath, sep=',')
            print("✅ CSV mit Komma-Trennung geladen")
        except pd.errors.ParserError:
            print("⚠️ Komma-Parser fehlgeschlagen, versuche alternative Methoden...")
            # Methode 2: Standard ohne explizites Trennzeichen
            try:
                df = pd.read_csv(csv_filepath)
                print("✅ CSV mit Standard-Einstellungen geladen")
            except pd.errors.ParserError:
                # Methode 3: Mit Semikolon als Trennzeichen
                try:
                    df = pd.read_csv(csv_filepath, sep=';')
                    print("✅ CSV mit Semikolon-Trennung geladen")
                except pd.errors.ParserError:
                    # Methode 4: Automatische Trennzeichen-Erkennung
                    try:
                        df = pd.read_csv(csv_filepath, sep=None, engine='python')
                        print("✅ CSV mit automatischer Trennzeichen-Erkennung geladen")
                    except pd.errors.ParserError:
                        # Methode 5: Mit error_bad_lines=False (ignoriert problematische Zeilen)
                        try:
                            df = pd.read_csv(csv_filepath, on_bad_lines='skip')
                            print("✅ CSV geladen (problematische Zeilen übersprungen)")
                        except pd.errors.ParserError:
                            # Methode 6: Als Text einlesen und erste Zeilen analysieren
                            print("🔍 Analysiere Datei-Struktur manuell...")
                        with open(csv_filepath, 'r', encoding='utf-8') as f:
                            lines = f.readlines()[:10]  # Erste 10 Zeilen
                        print("📋 Erste 10 Zeilen der Datei:")
                        for i, line in enumerate(lines):
                            print(f"  {i+1:2d}: {line.strip()}")
                        # Häufigste Trennzeichen ermitteln
                        separators = [',', ';', '\t', '|', ' ']
                        sep_counts = {}
                        for sep in separators:
                            count = sum(line.count(sep) for line in lines)
                            if count > 0:
                                sep_counts[sep] = count
                        if sep_counts:
                            best_sep = max(sep_counts, key=sep_counts.get)
                            print(f"🎯 Erkanntes Trennzeichen: '{best_sep}' ({sep_counts[best_sep]} Vorkommen)")
                            try:
                                df = pd.read_csv(csv_filepath, sep=best_sep, on_bad_lines='skip')
                                print("✅ CSV mit erkanntem Trennzeichen geladen")
                            except:
                                raise Exception("Alle CSV-Parsing-Methoden fehlgeschlagen")
                        else:
                            raise Exception("Kein gültiges Trennzeichen erkannt")

        # Nach erfolgreichem Laden: DateTime und GPS_DateTime in datetime konvertieren
        if df is not None:
            for spalte in ['DateTime', 'GPS_DateTime']:
                if spalte in df.columns:
                    df[spalte] = pd.to_datetime(df[spalte], errors='coerce')
        
        if df is None:
            raise Exception("CSV-Datei konnte nicht geladen werden")
        
        # Output-Dateiname erstellen (immer .txt-Endung!)
        base_name = os.path.splitext(csv_filepath)[0]
        info_filename = f"{base_name}_info.txt"
        
        # Info-String aufbauen
        info_content = []
        info_content.append("="*80)
        filename = os.path.basename(csv_filepath)
        info_content.append(f"CSV ANALYSE REPORT - {filename}")
        timestamp = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        info_content.append(f"Erstellt am: {timestamp}")
        info_content.append("="*80)
        
        # 1. GRUNDLEGENDE INFORMATIONEN
        info_content.append("\n🔍 1. GRUNDLEGENDE INFORMATIONEN")
        info_content.append("-" * 40)
        info_content.append(
            f"📊 Shape: {df.shape[0]} Zeilen × {df.shape[1]} Spalten"
        )
        file_size_kb = os.path.getsize(csv_filepath) / 1024
        info_content.append(f"💾 Dateigröße: {file_size_kb:.1f} KB")
        info_content.append(f"🔢 Gesamt-Datenpunkte: {df.size:,}")
        
        # 2. SPALTEN MIT DATENTYPEN
        info_content.append("\n📋 2. SPALTEN MIT DATENTYPEN")
        info_content.append("-" * 40)
        for i, (col, dtype) in enumerate(df.dtypes.items(), 1):
            # 5 zufällige unterschiedliche Beispielwerte anzeigen
            unique_values = df[col].dropna().unique()
            if len(unique_values) > 0:
                sample_size = min(5, len(unique_values))
                sample_values = np.random.choice(unique_values,
                                                 size=sample_size,
                                                 replace=False)
                sample_str = ", ".join([
                    str(val)[:25] + "..." if len(str(val)) > 25
                    else str(val) for val in sample_values
                ])
                info_content.append(
                    f"{i:2d}. {col:<25} → {str(dtype):<12} | "
                    f"Beispiele: {sample_str}"
                )
            else:
                info_content.append(
                    f"{i:2d}. {col:<25} → {str(dtype):<12} | "
                    f"Beispiele: (keine Werte)"
                )
        
        # 3. ERSTE 5 ZEILEN (HEAD)
        info_content.append("\n👀 3. ERSTE 5 ZEILEN (HEAD)")
        info_content.append("-" * 40)
        head_str = df.head().to_string(max_cols=None, max_colwidth=25)
        info_content.append(head_str)
        
        # LETZTE 5 ZEILEN (TAIL)
        info_content.append("\n👁️ LETZTE 5 ZEILEN (TAIL)")
        info_content.append("-" * 40)
        tail_str = df.tail().to_string(max_cols=None, max_colwidth=25)
        info_content.append(tail_str)
        
        # 4. INFO() EQUIVALENT
        info_content.append("\n📊 4. DATAFRAME INFO")
        info_content.append("-" * 40)
        info_content.append(f"RangeIndex: {len(df)} entries, 0 to {len(df)-1}")
        info_content.append(f"Data columns (total {len(df.columns)} columns):")
        
        for i, col in enumerate(df.columns):
            non_null_count = df[col].count()
            dtype = df[col].dtype
            info_content.append(
                f" {i:2d}  {col:<20} {non_null_count:>6} non-null  "
                f"{str(dtype)}"
            )
        
        memory_usage = df.memory_usage(deep=True).sum()
        info_content.append(f"Memory usage: {memory_usage / 1024:.1f} KB")
        
        # 5. NULL VALUES
        info_content.append("\n❌ 5. NULL VALUES (FEHLENDE WERTE)")
        info_content.append("-" * 40)
        null_counts = df.isnull().sum()
        total_nulls = null_counts.sum()
        
        if total_nulls == 0:
            info_content.append("✅ Keine fehlenden Werte gefunden!")
        else:
            info_content.append(f"🚨 Gesamt fehlende Werte: {total_nulls:,}")
            info_content.append("")
            for col, null_count in null_counts.items():
                if null_count > 0:
                    percentage = (null_count / len(df)) * 100
                    # Zeilennummern mit NULL-Werten finden
                    null_rows = df[df[col].isnull()].index.tolist()
                    
                    # Nur erste 10 Zeilennummern anzeigen, falls zu viele
                    if len(null_rows) <= 10:
                        rows_str = ", ".join(map(str, null_rows))
                    else:
                        first_10 = ", ".join(map(str, null_rows[:10]))
                        rows_str = (f"{first_10}, ... "
                                    f"(+{len(null_rows)-10} weitere)")
                    
                    info_content.append(
                        f"{col:<25}: {null_count:>6} ({percentage:.1f}%) | "
                        f"Zeilen: {rows_str}"
                    )
                    
                    # Zeige 2 Beispielzeilen mit NULL-Werten
                    sample_null_rows = null_rows[:2]  # Erste 2 Zeilen mit NULL
                    if sample_null_rows:
                        info_content.append(
                            f"   📋 Beispiel-Zeilen mit NULL in '{col}':"
                        )
                        for row_idx in sample_null_rows:
                            row_data = df.iloc[row_idx]
                            # Zeige nur die ersten 5 Spalten für Übersicht
                            row_preview = []
                            for i, (col_name, value) in enumerate(
                                row_data.items()
                            ):
                                if i >= 5:  # Nur erste 5 Spalten
                                    row_preview.append("...")
                                    break
                                if pd.isna(value):
                                    row_preview.append(f"{col_name}=NULL")
                                else:
                                    val_str = str(value)[:20]
                                    if len(str(value)) > 20:
                                        val_str += "..."
                                    row_preview.append(f"{col_name}={val_str}")
                            
                            info_content.append(
                                f"      Zeile {row_idx}: "
                                f"{' | '.join(row_preview)}"
                            )
                        info_content.append("")  # Leerzeile nach Beispielen
        
        # 6. NUMERISCHE STATISTIKEN
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            info_content.append("\n🔢 6. NUMERISCHE STATISTIKEN")
            info_content.append("-" * 40)
            desc = df[numeric_cols].describe()
            desc_str = desc.to_string()
            info_content.append(desc_str)
        
        # 7. KATEGORISCHE SPALTEN ANALYSE
        categorical_cols = df.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            info_content.append("\n📝 7. KATEGORISCHE SPALTEN ANALYSE")
            info_content.append("-" * 40)
            for col in categorical_cols:
                unique_count = df[col].nunique()
                mode_values = df[col].mode()
                most_common = (mode_values.iloc[0] if len(mode_values) > 0
                               else "N/A")
                info_content.append(
                    f"{col:<25}: {unique_count:>4} eindeutige Werte, "
                    f"häufigster: '{most_common}'"
                )
        
        # 8. ZUSÄTZLICHE WICHTIGE INFORMATIONEN
        info_content.append("\n⭐ 8. ZUSÄTZLICHE INFORMATIONEN")
        info_content.append("-" * 40)
        
        # Duplikate
        duplicate_count = df.duplicated().sum()
        info_content.append(f"🔁 Duplikate: {duplicate_count}")
        
        # Komplett leere Zeilen
        empty_rows = df.isnull().all(axis=1).sum()
        info_content.append(f"📭 Komplett leere Zeilen: {empty_rows}")
        
        # Spalten mit nur einem Wert
        single_value_cols = [col for col in df.columns if df[col].nunique() <= 1]
        if single_value_cols:
            info_content.append(f"⚠️  Spalten mit nur einem Wert: {', '.join(single_value_cols)}")
        
        # Korrelationen (nur für numerische Spalten)
        if len(numeric_cols) > 1:
            info_content.append("\n🔗 9. KORRELATIONEN (NUMERISCHE SPALTEN)")
            info_content.append("-" * 40)
            corr_matrix = df[numeric_cols].corr()
            
            # Höchste Korrelationen finden
            high_corr_pairs = []
            korrelationsschwelle = getattr(CONFIG, 'KORRELATIONSSCHWELLE_HOCH', 0.7)
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    corr_val = corr_matrix.iloc[i, j]
                    if abs(corr_val) > korrelationsschwelle:  # Hohe Korrelation (Schwelle aus config)
                        col1, col2 = corr_matrix.columns[i], corr_matrix.columns[j]
                        high_corr_pairs.append(f"{col1} ↔ {col2}: {corr_val:.3f}")
            
            if high_corr_pairs:
                info_content.append("🔥 Hohe Korrelationen (|r| > 0.7):")
                for pair in high_corr_pairs:
                    info_content.append(f"  {pair}")
            else:
                info_content.append("✅ Keine sehr hohen Korrelationen gefunden")
        
        # 10. ERWEITERTE SENSOR-ANALYSEN (NEU!)
        erweiterte_ergebnisse = {}
        if len(numeric_cols) >= 2:
            info_content.append("\n🔬 10. ERWEITERTE SENSOR-ANALYSEN")
            info_content.append("-" * 40)
            
            try:
                base_name = os.path.splitext(csv_filepath)[0]
                erweiterte_ergebnisse = erweiterte_sensor_analyse(df, base_name)
                
                # Cluster-Ergebnisse in Info einbauen
                if 'mq_cluster' in erweiterte_ergebnisse:
                    cluster_info = erweiterte_ergebnisse['mq_cluster']
                    if 'sensor_gruppen' in cluster_info:
                        info_content.append("🎯 MQ-Sensor Clustering:")
                        for gruppe, sensoren in cluster_info['sensor_gruppen'].items():
                            info_content.append(f"   {gruppe}: {', '.join(sensoren)}")
                
                # PCA-Ergebnisse
                if 'pca_analyse' in erweiterte_ergebnisse:
                    pca_info = erweiterte_ergebnisse['pca_analyse'] 
                    if 'erklaerte_varianz' in pca_info:
                        info_content.append("\n📊 Hauptkomponentenanalyse:")
                        for i, varianz in enumerate(pca_info['erklaerte_varianz']):
                            info_content.append(f"   Komponente {i+1}: {varianz:.1%} Varianz")
                
                # Zeitreihen-Ergebnisse
                if 'zeitreihen_analyse' in erweiterte_ergebnisse:
                    zeit_info = erweiterte_ergebnisse['zeitreihen_analyse']
                    if 'variable_sensoren' in zeit_info:
                        info_content.append(f"\n⏰ Variable Sensoren: {len(zeit_info['variable_sensoren'])}")
                        for sensor in zeit_info['variable_sensoren'][:3]:
                            info_content.append(f"   {sensor} (hoch variabel)")
                
                # Feature Selection
                if 'feature_selection' in erweiterte_ergebnisse:
                    feature_info = erweiterte_ergebnisse['feature_selection']
                    if 'empfohlene_sensoren' in feature_info:
                        info_content.append(f"\n🎯 Empfohlene unabhängige Sensoren:")
                        for sensor in feature_info['empfohlene_sensoren'][:5]:
                            info_content.append(f"   {sensor}")
                            
            except Exception as e:
                info_content.append(f"⚠️ Erweiterte Analyse fehlgeschlagen: {str(e)}")
                print(f"⚠️ Erweiterte Analyse-Fehler: {e}")

        # 11. ZUSAMMENFASSUNG
        info_content.append("\n📈 11. ZUSAMMENFASSUNG")
        info_content.append("-" * 40)
        data_quality = ((df.size - total_nulls) / df.size * 100)
        info_content.append(f"✅ Datenqualität: {data_quality:.1f}% vollständig")
        info_content.append(
            f"📊 Datentypen: {len(numeric_cols)} numerisch, "
            f"{len(categorical_cols)} kategorisch"
        )
        uniqueness = (1 - duplicate_count/len(df)) * 100
        info_content.append(
            f"🔍 Einzigartigkeit: {uniqueness:.1f}% eindeutige Zeilen"
        )
        
        # Erweiterte Analyse Zusammenfassung
        if erweiterte_ergebnisse:
            info_content.append(f"🔬 Erweiterte Analysen: {len(erweiterte_ergebnisse)} Module")
            
            # Empfehlungen basierend auf Analysen
            empfehlungen = []
            if 'mq_cluster' in erweiterte_ergebnisse:
                cluster_anzahl = erweiterte_ergebnisse['mq_cluster'].get('cluster_anzahl', 0)
                empfehlungen.append(f"{cluster_anzahl} MQ-Sensor-Gruppen identifiziert")
            
            if 'feature_selection' in erweiterte_ergebnisse:
                unabhaengige = len(erweiterte_ergebnisse['feature_selection'].get('unabhaengige_sensoren', []))
                empfehlungen.append(f"{unabhaengige} unabhängige Sensoren empfohlen")
            
            if empfehlungen:
                info_content.append("💡 Analyse-Empfehlungen:")
                for emp in empfehlungen:
                    info_content.append(f"   • {emp}")
        

        # Speichern nur noch in den beiden Zielorten im ergebnisse-Ordner
        # (Kein Speichern mehr im Originalpfad)

        # 1. Kopie im Ordner ergebnisse mit info_txt_{alter dateiname}
        ergebnisse_ordner = r"E:/dev/projekt_python_venv/airscout-analytics/data/ergebnisse"
        os.makedirs(ergebnisse_ordner, exist_ok=True)
        alt_dateiname = os.path.basename(csv_filepath)
        info_txt_name = f"info_txt_{alt_dateiname}".replace('.csv', '.txt')
        info_txt_path = os.path.join(ergebnisse_ordner, info_txt_name)
        with open(info_txt_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(info_content))

        # 2. Kopie im Unterordner yyyy_mm_dd_hh_mm mit {alter dateiname}_info.txt
        # Extrahiere Zeitstempel aus Dateinamen (Format: yyyy_mm_dd_hh_mm)
        match = re.search(r'(\d{4})_(\d{2})(\d{2})(\d{2})(\d{2})', alt_dateiname)
        if match:
            yyyy_mm_dd_hh_mm = f"{match.group(1)}_{match.group(2)}_{match.group(3)}_{match.group(4)}_{match.group(5)}"
        else:
            yyyy_mm_dd_hh_mm = os.path.splitext(alt_dateiname)[0]
        unterordner = os.path.join(ergebnisse_ordner, yyyy_mm_dd_hh_mm)
        os.makedirs(unterordner, exist_ok=True)
        info_unterordner_name = f"{os.path.splitext(alt_dateiname)[0]}_info.txt"
        info_unterordner_path = os.path.join(unterordner, info_unterordner_name)
        with open(info_unterordner_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(info_content))

        print("✅ Analyse abgeschlossen!")
        print(f"📁 Info-Datei erstellt: {info_txt_path}")
        print(f"📁 Kopie gespeichert als: {info_unterordner_path}")
        print(f"📊 {len(info_content)} Zeilen Analyse-Information gespeichert")

        # Rückgabe: immer .txt-Endung, nicht .csv
        return info_txt_path
        
    except FileNotFoundError:
        print(f"❌ Datei nicht gefunden: {csv_filepath}")
        return None
    except pd.errors.EmptyDataError:
        print(f"❌ Die Datei ist leer: {csv_filepath}")
        return None
    except pd.errors.ParserError as e:
        print(f"❌ Fehler beim Parsen der CSV-Datei: {e}")
        return None
    except Exception as e:
        print(f"❌ Fehler beim Analysieren der CSV-Datei: {e}")
        return None


# 🚀 SCRIPT VERWENDUNG:
if __name__ == "__main__":

    print("🚀 CSV INFO EXTRACTOR")
    print("="*50)

    # Automatische Suche nach erster CSV in data/bearbeitet0
    import glob
    import sys
    csv_ordner = r"E:/dev/projekt_python_venv/airscout-analytics/data/bearbeitet0"
    csv_files = glob.glob(os.path.join(csv_ordner, "*.csv"))
    if csv_files:
        csv_file = csv_files[0]
        print(f"📂 Automatisch gefundene Datei: {csv_file}")
    else:
        print(f"❌ Keine CSV-Datei in {csv_ordner} gefunden!")
        sys.exit(1)

    # Script ausführen
    result = csv_info_extractor(csv_file)

    if result:
        print(f"\n🎯 Fertig! Alle Informationen wurden in '{result}' gespeichert.")
        print("\n💡 Das Script kann für jede CSV-Datei verwendet werden:")
        print("   python csv_analyzer_02.py <pfad/zur/datei.csv>")
    else:
        print("\n❌ Analyse konnte nicht abgeschlossen werden.")


def erweiterte_sensor_analyse(df: pd.DataFrame, output_pfad: str) -> dict:
    """
    Führt erweiterte Analysen für Sensor-Daten durch.
    
    Diese Funktion implementiert verschiedene Machine Learning Techniken
    zur Analyse von Sensordaten, insbesondere für MQ-Gassensoren.
    
    :param df: DataFrame mit Sensordaten
    :type df: pd.DataFrame
    :param output_pfad: Pfad für die Ausgabe-Dateien
    :type output_pfad: str
    :returns: Dictionary mit Analyseergebnissen
    :rtype: dict
    :raises ValueError: Wenn keine numerischen Spalten gefunden werden
    :example:
    
        >>> ergebnisse = erweiterte_sensor_analyse(df, 'C:/output/')
        >>> print(ergebnisse['mq_cluster'])
        
    """
    print("\n🔬 ERWEITERTE SENSOR-ANALYSE")
    print("=" * 50)
    
    # Numerische Spalten identifizieren
    numerische_spalten = df.select_dtypes(include=[np.number]).columns.tolist()
    if len(numerische_spalten) < 2:
        print("❌ Nicht genügend numerische Spalten für erweiterte Analyse")
        return {}
    
    # MQ-Sensoren identifizieren (spalten mit 'MQ' oder 'mq' im Namen)
    mq_spalten = [col for col in numerische_spalten 
                  if 'mq' in col.lower() or 'gas' in col.lower()]
    
    ergebnisse = {}
    
    # 1. CLUSTERANALYSE DER MQ-SENSOREN
    if len(mq_spalten) >= 2:
        ergebnisse['mq_cluster'] = mq_sensor_clustering(df, mq_spalten, output_pfad)
    
    # 2. PCA (HAUPTKOMPONENTENANALYSE)
    if len(numerische_spalten) >= 3:
        ergebnisse['pca_analyse'] = hauptkomponenten_analyse(df, numerische_spalten, output_pfad)
    
    # 3. ZEITREIHENANALYSE
    ergebnisse['zeitreihen_analyse'] = zeitreihen_veraenderungs_analyse(df, numerische_spalten, output_pfad)
    
    # 4. FEATURE SELECTION
    if len(numerische_spalten) >= 3:
        ergebnisse['feature_selection'] = unabhaengige_sensoren_waehlen(df, numerische_spalten, output_pfad)
    
    return ergebnisse


def mq_sensor_clustering(df: pd.DataFrame, mq_spalten: list, output_pfad: str) -> dict:
    """
    Führt Clusteranalyse der MQ-Sensoren durch.
    
    **Methode KMeans()** gruppiert Sensoren basierend auf ihrem Verhalten
    **Argument n_clusters** bestimmt die Anzahl der Gruppen
    **StandardScaler()** normalisiert die Sensor-Werte für bessere Vergleichbarkeit
    **Rückgabewert** ist ein Dictionary mit Cluster-Informationen und Gruppierungen
    
    :param df: DataFrame mit Sensordaten
    :type df: pd.DataFrame  
    :param mq_spalten: Liste der MQ-Sensor Spaltennamen
    :type mq_spalten: list
    :param output_pfad: Pfad für Ausgabe-Dateien
    :type output_pfad: str
    :returns: Dictionary mit Cluster-Ergebnissen
    :rtype: dict
    """
    print("\n🎯 1. CLUSTERANALYSE DER MQ-SENSOREN")
    print("-" * 40)
    
    # Daten für Clustering vorbereiten
    mq_daten = df[mq_spalten].dropna()
    if len(mq_daten) < 10:
        print("⚠️ Zu wenige Datenpunkte für Clustering")
        return {}
    
    # Daten standardisieren (wichtig für K-Means!)
    scaler = StandardScaler()
    mq_standardisiert = scaler.fit_transform(mq_daten)
    
    # Optimale Cluster-Anzahl mit Elbow-Methode finden
    max_cluster = min(8, len(mq_spalten))
    inertien = []
    
    for k in range(2, max_cluster + 1):
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(mq_standardisiert)
        inertien.append(kmeans.inertia_)
    
    # Optimale Anzahl wählen (vereinfacht: mittlerer Wert)
    optimale_cluster = len(inertien) // 2 + 2
    
    # Finales Clustering
    kmeans_final = KMeans(n_clusters=optimale_cluster, random_state=42, n_init=10)
    cluster_labels = kmeans_final.fit_predict(mq_standardisiert)
    
    # Ergebnisse zusammenstellen
    cluster_info = {}
    for cluster_id in range(optimale_cluster):
        sensoren_in_cluster = [mq_spalten[i] for i, label in enumerate(cluster_labels) 
                              if label == cluster_id]
        cluster_info[f"Gruppe_{cluster_id + 1}"] = sensoren_in_cluster
    
    print(f"✅ {optimale_cluster} Sensor-Gruppen identifiziert:")
    for gruppe, sensoren in cluster_info.items():
        print(f"   {gruppe}: {', '.join(sensoren)}")
    
    return {
        'cluster_anzahl': optimale_cluster,
        'sensor_gruppen': cluster_info,
        'cluster_zentren': kmeans_final.cluster_centers_
    }


def hauptkomponenten_analyse(df: pd.DataFrame, numerische_spalten: list, output_pfad: str) -> dict:
    """
    Führt PCA (Hauptkomponentenanalyse) durch zur Dimensionsreduktion.
    
    **Methode PCA()** reduziert die Anzahl der Sensor-Dimensionen auf die wichtigsten
    **Argument n_components** bestimmt, auf wie viele Hauptkomponenten reduziert wird
    **explained_variance_ratio_** zeigt, wie viel Varianz jede Komponente erklärt
    **Rückgabewert** ist ein Dictionary mit den Hauptkomponenten und deren Wichtigkeit
    
    :param df: DataFrame mit Sensordaten
    :type df: pd.DataFrame
    :param numerische_spalten: Liste numerischer Spaltennamen  
    :type numerische_spalten: list
    :param output_pfad: Pfad für Ausgabe-Dateien
    :type output_pfad: str
    :returns: Dictionary mit PCA-Ergebnissen
    :rtype: dict
    """
    print("\n📊 2. HAUPTKOMPONENTENANALYSE (PCA)")
    print("-" * 40)
    
    # Daten vorbereiten
    sensor_daten = df[numerische_spalten].dropna()
    if len(sensor_daten) < 10:
        print("⚠️ Zu wenige Datenpunkte für PCA")
        return {}
    
    # Daten standardisieren
    scaler = StandardScaler()
    daten_standardisiert = scaler.fit_transform(sensor_daten)
    
    # PCA auf konfigurierbare Anzahl Komponenten reduzieren
    pca_komponenten_anzahl = getattr(CONFIG, 'PCA_KOMPONENTEN_ANZAHL', 3)
    komponenten_anzahl = min(pca_komponenten_anzahl, len(numerische_spalten))
    pca = PCA(n_components=komponenten_anzahl)
    hauptkomponenten = pca.fit_transform(daten_standardisiert)
    
    # Erklärte Varianz berechnen
    erklaerte_varianz = pca.explained_variance_ratio_
    kumulierte_varianz = np.cumsum(erklaerte_varianz)
    
    print(f"✅ {komponenten_anzahl} Hauptkomponenten extrahiert:")
    for i, (varianz, kumuliert) in enumerate(zip(erklaerte_varianz, kumulierte_varianz)):
        print(f"   Komponente {i+1}: {varianz:.1%} Varianz ({kumuliert:.1%} kumuliert)")
    
    # Wichtigste Sensoren pro Komponente identifizieren
    komponenten_matrix = pca.components_
    wichtige_sensoren = {}
    
    for i in range(komponenten_anzahl):
        # Absolute Werte der Ladungen für diese Komponente
        ladungen = np.abs(komponenten_matrix[i])
        # Sortiere Sensoren nach Wichtigkeit
        wichtigkeits_indices = np.argsort(ladungen)[::-1]
        top_sensoren = [numerische_spalten[idx] for idx in wichtigkeits_indices[:3]]
        wichtige_sensoren[f"Komponente_{i+1}"] = top_sensoren
        
        print(f"   Top 3 Sensoren Komp. {i+1}: {', '.join(top_sensoren)}")
    
    return {
        'komponenten_anzahl': komponenten_anzahl,
        'erklaerte_varianz': erklaerte_varianz.tolist(),
        'kumulierte_varianz': kumulierte_varianz.tolist(),
        'wichtige_sensoren': wichtige_sensoren,
        'transformierte_daten': hauptkomponenten
    }


def zeitreihen_veraenderungs_analyse(df: pd.DataFrame, numerische_spalten: list, output_pfad: str) -> dict:
    """
    Analysiert zeitliche Veränderungen in Sensor-Daten.
    
    **Methode diff()** berechnet die Differenzen zwischen aufeinanderfolgenden Messungen
    **rolling().mean()** erstellt gleitende Durchschnitte zur Trend-Erkennung
    **std()** misst die Variabilität der Sensor-Werte
    **Rückgabewert** ist ein Dictionary mit Trend- und Variabilitäts-Informationen
    
    :param df: DataFrame mit Sensordaten
    :type df: pd.DataFrame
    :param numerische_spalten: Liste numerischer Spaltennamen
    :type numerische_spalten: list  
    :param output_pfad: Pfad für Ausgabe-Dateien
    :type output_pfad: str
    :returns: Dictionary mit Zeitreihen-Analyseergebnissen
    :rtype: dict
    """
    print("\n⏰ 3. ZEITREIHENANALYSE")
    print("-" * 40)
    
    if len(df) < 20:
        print("⚠️ Zu wenige Datenpunkte für Zeitreihenanalyse")
        return {}
    
    # Veränderungsraten berechnen (erste Ableitung)
    veraenderungen = {}
    variabilitaet = {}
    trends = {}
    
    for spalte in numerische_spalten:
        sensor_werte = df[spalte].dropna()
        if len(sensor_werte) < 10:
            continue
            
        # Absolute Veränderungen zwischen aufeinanderfolgenden Messungen
        differenzen = sensor_werte.diff().dropna()
        durchschnittliche_veraenderung = differenzen.mean()
        variabilitaet_sensor = differenzen.std()
        
        # Trend über gleitenden Durchschnitt (letzte 10% der Daten)
        fenster_groesse = max(5, len(sensor_werte) // 10)
        gleitender_durchschnitt = sensor_werte.rolling(window=fenster_groesse).mean()
        trend_richtung = "steigend" if gleitender_durchschnitt.iloc[-1] > gleitender_durchschnitt.iloc[-fenster_groesse] else "fallend"
        
        veraenderungen[spalte] = durchschnittliche_veraenderung
        variabilitaet[spalte] = variabilitaet_sensor
        trends[spalte] = trend_richtung
    
    # Sensoren nach Variabilität sortieren
    sortierte_variabilitaet = sorted(variabilitaet.items(), key=lambda x: x[1], reverse=True)
    
    print("✅ Sensor-Variabilität (höchste zuerst):")
    for sensor, var in sortierte_variabilitaet[:5]:  # Top 5
        trend = trends.get(sensor, "unbekannt")
        print(f"   {sensor}: Variabilität={var:.3f}, Trend={trend}")
    
    # Signifikante Veränderungen identifizieren
    variabilitaetsfaktor = getattr(CONFIG, 'VARIABILITAETSFAKTOR', 1.5)
    signifikante_sensoren = [sensor for sensor, var in variabilitaet.items() 
                           if var > np.mean(list(variabilitaet.values())) * variabilitaetsfaktor]
    
    print(f"\n🔥 {len(signifikante_sensoren)} Sensoren mit hoher Variabilität:")
    for sensor in signifikante_sensoren:
        print(f"   {sensor} (möglicherweise umwelt-sensitiv)")
    
    return {
        'veraenderungsraten': veraenderungen,
        'variabilitaet': variabilitaet,
        'trends': trends,
        'variable_sensoren': signifikante_sensoren,
        'stabilste_sensoren': [s for s, v in sorted(variabilitaet.items(), key=lambda x: x[1])[:3]]
    }


def unabhaengige_sensoren_waehlen(df: pd.DataFrame, numerische_spalten: list, output_pfad: str) -> dict:
    """
    Wählt Sensoren mit maximaler Unabhängigkeit aus.
    
    **Methode corr()** berechnet Korrelationsmatrix zwischen allen Sensoren
    **SelectKBest** wählt die besten Features basierend auf statistischen Tests
    **mutual_info_regression** misst nichtlineare Abhängigkeiten zwischen Variablen
    **Rückgabewert** ist ein Dictionary mit den unabhängigsten Sensoren
    
    :param df: DataFrame mit Sensordaten
    :type df: pd.DataFrame
    :param numerische_spalten: Liste numerischer Spaltennamen
    :type numerische_spalten: list
    :param output_pfad: Pfad für Ausgabe-Dateien  
    :type output_pfad: str
    :returns: Dictionary mit Feature-Selection Ergebnissen
    :rtype: dict
    """
    print("\n🎯 4. FEATURE SELECTION (UNABHÄNGIGE SENSOREN)")
    print("-" * 40)
    
    sensor_daten = df[numerische_spalten].dropna()
    if len(sensor_daten) < 10:
        print("⚠️ Zu wenige Datenpunkte für Feature Selection")
        return {}
    
    # Korrelationsmatrix berechnen
    korrelations_matrix = sensor_daten.corr()
    
    # Hoch korrelierte Sensor-Paare finden
    hohe_korrelationen = []
    korrelationsschwelle_sehr_hoch = getattr(CONFIG, 'KORRELATIONSSCHWELLE_SEHR_HOCH', 0.8)
    for i in range(len(korrelations_matrix.columns)):
        for j in range(i+1, len(korrelations_matrix.columns)):
            korr_wert = korrelations_matrix.iloc[i, j]
            if abs(korr_wert) > korrelationsschwelle_sehr_hoch:  # Sehr hohe Korrelation (Schwelle aus config)
                sensor1 = korrelations_matrix.columns[i]
                sensor2 = korrelations_matrix.columns[j]
                hohe_korrelationen.append((sensor1, sensor2, korr_wert))
    
    # Redundante Sensoren identifizieren
    redundante_sensoren = set()
    for sensor1, sensor2, korr in hohe_korrelationen:
        # Sensor mit geringerer Varianz als redundant markieren
        var1 = sensor_daten[sensor1].var()
        var2 = sensor_daten[sensor2].var()
        redundanter_sensor = sensor1 if var1 < var2 else sensor2
        redundante_sensoren.add(redundanter_sensor)

    # Unabhängige Sensoren auswählen
    unabhaengige_sensoren = [s for s in numerische_spalten if s not in redundante_sensoren]

    # Diversität bewerten (durchschnittliche absolute Korrelation)
    if len(unabhaengige_sensoren) > 1:
        unabhaengige_korr_matrix = sensor_daten[unabhaengige_sensoren].corr()
        durchschnittliche_korrelation = np.abs(unabhaengige_korr_matrix.values).mean()
    else:
        durchschnittliche_korrelation = 0.0

    print(f"✅ {len(hohe_korrelationen)} redundante Sensor-Paare gefunden:")
    for sensor1, sensor2, korr in hohe_korrelationen[:5]:  # Erste 5 zeigen
        print(f"   {sensor1} ↔ {sensor2}: r={korr:.3f}")

    print(f"\n🎯 {len(unabhaengige_sensoren)} unabhängige Sensoren ausgewählt:")
    for sensor in unabhaengige_sensoren:
        print(f"   {sensor}")

    print(f"\n📊 Durchschnittliche Korrelation der Auswahl: {durchschnittliche_korrelation:.3f}")

    return {
        'unabhaengige_sensoren': unabhaengige_sensoren,
        'redundante_sensoren': list(redundante_sensoren),
        'hohe_korrelationen': hohe_korrelationen,
        'durchschnittliche_korrelation': durchschnittliche_korrelation,
        'empfohlene_sensoren': unabhaengige_sensoren[:8]  # Top 8 für praktische Nutzung
    }

