"""📊 CSV ANALYSE UND INFO-EXPORT SCRIPT"""
import pandas as pd
import numpy as np
import os
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages

# Erweiterte Imports für neue Statistiken mit detaillierter Fehlerprüfung
missing_libs = []
ADVANCED_LIBS_AVAILABLE = True

try:
    from scipy.optimize import minimize
    from scipy.stats import zscore
except ImportError:
    missing_libs.append("scipy")
    ADVANCED_LIBS_AVAILABLE = False

try:
    from sklearn.linear_model import LinearRegression
except ImportError:
    missing_libs.append("scikit-learn")
    ADVANCED_LIBS_AVAILABLE = False

try:
    import statsmodels.api as sm
except ImportError:
    missing_libs.append("statsmodels")
    ADVANCED_LIBS_AVAILABLE = False

# Informative Ausgabe über fehlende Bibliotheken
if not ADVANCED_LIBS_AVAILABLE:
    print("⚠️ FEHLENDE BIBLIOTHEKEN FÜR ERWEITERTE STATISTIKEN:")
    print("-" * 60)
    for lib in missing_libs:
        print(f"❌ {lib}")
    print("\n📦 INSTALLATION:")
    print("Führe folgenden Befehl aus:")
    install_cmd = f"pip install {' '.join(missing_libs)}"
    print(f"   {install_cmd}")
    print("\n🔧 ALTERNATIVE (falls pip Probleme hat):")
    print("   conda install scipy scikit-learn statsmodels")
    print("\n💡 NACH INSTALLATION:")
    print("   Script erneut ausführen für erweiterte Analysen")
    print("-" * 60)

def advanced_statistics_analysis(df):
    """
    Führt erweiterte statistische Analysen durch
    """
    analysis_results = []
    
    if not ADVANCED_LIBS_AVAILABLE:
        analysis_results.append("⚠️ ERWEITERTE STATISTIKEN NICHT VERFÜGBAR")
        analysis_results.append("📦 Fehlende Bibliotheken:")
        for lib in missing_libs:
            analysis_results.append(f"   ❌ {lib}")
        analysis_results.append(f"\n🛠️ Installation: pip install {' '.join(missing_libs)}")
        analysis_results.append("🔄 Nach Installation Script erneut ausführen")
        return analysis_results
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    if len(numeric_cols) < 2:
        analysis_results.append("⚠️ Mindestens 2 numerische Spalten für erweiterte Analysen erforderlich")
        return analysis_results
    
    # 1. FORENSISCHE STATISTIK - Anomalieerkennung
    analysis_results.append("\n🔍 FORENSISCHE STATISTIK - ANOMALIEERKENNUNG")
    analysis_results.append("-" * 50)
    
    try:
        for col in numeric_cols[:3]:  # Analysiere erste 3 numerische Spalten
            if df[col].std() > 0:  # Vermeidie Division durch 0
                z_scores = np.abs(zscore(df[col].dropna()))
                anomalies = np.sum(z_scores > 3)
                if anomalies > 0:
                    anomaly_percentage = (anomalies / len(df)) * 100
                    analysis_results.append(
                        f"🚨 {col}: {anomalies} Anomalien ({anomaly_percentage:.1f}%) mit |z-score| > 3"
                    )
                else:
                    analysis_results.append(f"✅ {col}: Keine Anomalien gefunden")
    except Exception as e:
        analysis_results.append(f"❌ Forensische Analyse fehlgeschlagen: {str(e)}")
    
    # 2. EXPLORATIVE STATISTIK - Verteilungsanalyse
    analysis_results.append("\n🧭 EXPLORATIVE STATISTIK - VERTEILUNGSANALYSE")
    analysis_results.append("-" * 50)
    
    try:
        for col in numeric_cols[:3]:
            data = df[col].dropna()
            if len(data) > 0:
                skewness = data.skew()
                kurtosis = data.kurtosis()
                
                # Verteilungsinterpretation
                if abs(skewness) < 0.5:
                    skew_interpretation = "symmetrisch"
                elif skewness > 0.5:
                    skew_interpretation = "rechtsschief"
                else:
                    skew_interpretation = "linksschief"
                
                if kurtosis > 3:
                    kurt_interpretation = "spitz (leptokurtisch)"
                elif kurtosis < 3:
                    kurt_interpretation = "flach (platykurtisch)"
                else:
                    kurt_interpretation = "normal (mesokurtisch)"
                
                analysis_results.append(
                    f"📊 {col}: Schiefe={skewness:.3f} ({skew_interpretation}), "
                    f"Kurtosis={kurtosis:.3f} ({kurt_interpretation})"
                )
    except Exception as e:
        analysis_results.append(f"❌ Explorative Analyse fehlgeschlagen: {str(e)}")
    
    # 3. PRÄDIKTIVE STATISTIK - Einfache Regression
    analysis_results.append("\n🔮 PRÄDIKTIVE STATISTIK - REGRESSIONSANALYSE")
    analysis_results.append("-" * 50)
    
    try:
        if len(numeric_cols) >= 2:
            # Wähle erste 2 numerische Spalten für Regression
            X_col = numeric_cols[0]
            y_col = numeric_cols[1]
            
            # Bereite Daten vor
            valid_data = df[[X_col, y_col]].dropna()
            if len(valid_data) > 5:  # Mindestens 5 Datenpunkte
                X = valid_data[[X_col]].values
                y = valid_data[y_col].values
                
                model = LinearRegression()
                model.fit(X, y)
                
                r_squared = model.score(X, y)
                coef = model.coef_[0]
                intercept = model.intercept_
                
                analysis_results.append(
                    f"📈 {y_col} = {intercept:.3f} + {coef:.3f} × {X_col}"
                )
                analysis_results.append(f"📊 R² = {r_squared:.3f} (Erklärte Varianz: {r_squared*100:.1f}%)")
                
                # Beispielprognose
                mean_x = X.mean()
                prediction = model.predict([[mean_x]])[0]
                analysis_results.append(
                    f"🎯 Prognose für {X_col}={mean_x:.2f}: {y_col}={prediction:.2f}"
                )
            else:
                analysis_results.append("⚠️ Zu wenige Datenpunkte für Regression")
    except Exception as e:
        analysis_results.append(f"❌ Prädiktive Analyse fehlgeschlagen: {str(e)}")
    
    # 4. DIAGNOSTISCHE STATISTIK - Korrelationsanalyse
    analysis_results.append("\n🧠 DIAGNOSTISCHE STATISTIK - KORRELATIONEN")
    analysis_results.append("-" * 50)
    
    try:
        if len(numeric_cols) >= 2:
            corr_matrix = df[numeric_cols].corr()
            
            # Finde höchste positive und negative Korrelationen
            high_corr_pairs = []
            for i in range(len(numeric_cols)):
                for j in range(i+1, len(numeric_cols)):
                    corr_val = corr_matrix.iloc[i, j]
                    if abs(corr_val) > 0.5:  # Mittlere bis hohe Korrelation
                        col1, col2 = numeric_cols[i], numeric_cols[j]
                        if corr_val > 0:
                            relationship = "positive Korrelation"
                        else:
                            relationship = "negative Korrelation"
                        high_corr_pairs.append(
                            f"🔗 {col1} ↔ {col2}: {corr_val:.3f} ({relationship})"
                        )
            
            if high_corr_pairs:
                analysis_results.extend(high_corr_pairs[:5])  # Top 5 Korrelationen
            else:
                analysis_results.append("📊 Keine starken Korrelationen (|r| > 0.5) gefunden")
    except Exception as e:
        analysis_results.append(f"❌ Diagnostische Analyse fehlgeschlagen: {str(e)}")
    
    # 5. KAUSALE STATISTIK - Regressionsmodell mit Statistiken
    analysis_results.append("\n🔄 KAUSALE STATISTIK - REGRESSIONSSTATISTIKEN")
    analysis_results.append("-" * 50)
    
    try:
        if len(numeric_cols) >= 3:
            # Multiple Regression mit ersten 3 numerischen Spalten
            target_col = numeric_cols[0]
            feature_cols = numeric_cols[1:3]
            
            valid_data = df[numeric_cols[:3]].dropna()
            if len(valid_data) > 10:  # Mindestens 10 Datenpunkte
                X = valid_data[feature_cols]
                X = sm.add_constant(X)  # Konstante hinzufügen
                y = valid_data[target_col]
                
                model = sm.OLS(y, X).fit()
                
                analysis_results.append(f"🎯 Abhängige Variable: {target_col}")
                analysis_results.append(f"🔢 R²: {model.rsquared:.3f}")
                analysis_results.append(f"📊 Adj. R²: {model.rsquared_adj:.3f}")
                analysis_results.append(f"🔍 F-Statistik: {model.fvalue:.3f}")
                
                # Koeffizienten mit Signifikanz
                for i, param in enumerate(model.params.index):
                    coef = model.params[param]
                    p_value = model.pvalues[param]
                    significance = "***" if p_value < 0.001 else "**" if p_value < 0.01 else "*" if p_value < 0.05 else ""
                    analysis_results.append(
                        f"   {param}: {coef:.3f} (p={p_value:.3f}) {significance}"
                    )
            else:
                analysis_results.append("⚠️ Zu wenige Datenpunkte für multiple Regression")
    except Exception as e:
        analysis_results.append(f"❌ Kausale Analyse fehlgeschlagen: {str(e)}")
    
    # 6. ZEITREIHENANALYSE (falls Datumsspalte vorhanden)
    analysis_results.append("\n⏳ ZEITREIHENANALYSE")
    analysis_results.append("-" * 50)
    
    try:
        # Suche nach Datumsspalten
        date_cols = []
        for col in df.columns:
            if df[col].dtype == 'object':
                # Versuche erste 5 Werte als Datum zu parsen
                sample_values = df[col].dropna().head()
                try:
                    pd.to_datetime(sample_values.iloc[0])
                    date_cols.append(col)
                except:
                    pass
        
        if date_cols and len(numeric_cols) > 0:
            date_col = date_cols[0]
            numeric_col = numeric_cols[0]
            
            # Konvertiere zu Datetime
            df_temp = df.copy()
            df_temp[date_col] = pd.to_datetime(df_temp[date_col], errors='coerce')
            df_temp = df_temp.dropna(subset=[date_col, numeric_col])
            
            if len(df_temp) > 5:
                df_temp = df_temp.sort_values(date_col)
                
                # Zeitspanne
                time_span = df_temp[date_col].max() - df_temp[date_col].min()
                analysis_results.append(f"📅 Zeitspanne: {time_span.days} Tage")
                
                # Trend (einfache lineare Regression über Zeit)
                df_temp['time_numeric'] = (df_temp[date_col] - df_temp[date_col].min()).dt.days
                X = df_temp[['time_numeric']].values
                y = df_temp[numeric_col].values
                
                if len(X) > 2:
                    model = LinearRegression()
                    model.fit(X, y)
                    trend_slope = model.coef_[0]
                    
                    if abs(trend_slope) < 0.001:
                        trend_direction = "stabil"
                    elif trend_slope > 0:
                        trend_direction = "steigend"
                    else:
                        trend_direction = "fallend"
                    
                    analysis_results.append(
                        f"📈 Trend für {numeric_col}: {trend_direction} "
                        f"(Steigung: {trend_slope:.6f}/Tag)"
                    )
        else:
            analysis_results.append("📅 Keine Datumsspalten für Zeitreihenanalyse gefunden")
    except Exception as e:
        analysis_results.append(f"❌ Zeitreihenanalyse fehlgeschlagen: {str(e)}")
    
    # 7. PRÄSKRIPTIVE STATISTIK - Einfache Optimierungsempfehlung
    analysis_results.append("\n🎯 PRÄSKRIPTIVE STATISTIK - OPTIMIERUNGSEMPFEHLUNGEN")
    analysis_results.append("-" * 50)
    
    try:
        if len(numeric_cols) >= 2:
            # Finde optimale Werte basierend auf Korrelationen
            target_col = numeric_cols[0]  # Zielwert (z.B. Umsatz)
            
            recommendations = []
            for col in numeric_cols[1:3]:  # Prüfe bis zu 2 andere Spalten
                corr = df[target_col].corr(df[col])
                if abs(corr) > 0.3:  # Relevante Korrelation
                    optimal_value = df.loc[df[target_col].idxmax(), col]
                    median_value = df[col].median()
                    
                    if corr > 0:
                        recommendation = f"erhöhen auf {optimal_value:.2f}"
                    else:
                        recommendation = f"reduzieren auf {optimal_value:.2f}"
                    
                    recommendations.append(
                        f"💡 {col}: {recommendation} "
                        f"(aktuell Median: {median_value:.2f}, Korr: {corr:.3f})"
                    )
            
            if recommendations:
                analysis_results.append(f"🎯 Zur Optimierung von {target_col}:")
                analysis_results.extend(recommendations)
            else:
                analysis_results.append("📊 Keine klaren Optimierungsempfehlungen ableitbar")
    except Exception as e:
        analysis_results.append(f"❌ Präskriptive Analyse fehlgeschlagen: {str(e)}")
    
    return analysis_results

def csv_info_extractor(csv_filepath):
    """
    Extrahiert alle wichtigen Informationen aus einer CSV-Datei
    und speichert sie in eine _info.txt-Datei und erstellt zusätzlich eine PDF-Auswertung.
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
        
        if df is None:
            raise Exception("CSV-Datei konnte nicht geladen werden")
        
        # Output-Dateiname erstellen
        base_name = os.path.splitext(csv_filepath)[0]
        info_filename = f"{base_name}_info.txt"
        pdf_filename = f"{base_name}_grafik.pdf"
        
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
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    corr_val = corr_matrix.iloc[i, j]
                    if abs(corr_val) > 0.7:  # Hohe Korrelation
                        col1, col2 = corr_matrix.columns[i], corr_matrix.columns[j]
                        high_corr_pairs.append(f"{col1} ↔ {col2}: {corr_val:.3f}")
            
            if high_corr_pairs:
                info_content.append("🔥 Hohe Korrelationen (|r| > 0.7):")
                for pair in high_corr_pairs:
                    info_content.append(f"  {pair}")
            else:
                info_content.append("✅ Keine sehr hohen Korrelationen gefunden")
        
        # *** NEUE ERWEITERTE STATISTIKEN HINZUFÜGEN ***
        advanced_results = advanced_statistics_analysis(df)
        info_content.append("\n" + "="*80)
        info_content.append("🚀 ERWEITERTE STATISTISCHE ANALYSEN")
        info_content.append("="*80)
        info_content.extend(advanced_results)
        
        # 10. ZUSAMMENFASSUNG
        info_content.append("\n📈 10. ZUSAMMENFASSUNG")
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
        
        # TXT-Ausgabe
        with open(info_filename, "w", encoding="utf-8") as f:
            for line in info_content:
                f.write(line + "\n")
        print("Analyse abgeschlossen!")
        print(f"Info-TXT erstellt: {info_filename}")
        print(f"{len(info_content)} Zeilen Analyse-Information gespeichert")
        # PDF-Auswertung
        erstelle_auswertungsdiagramme(csv_filepath)
        print(f"PDF-Auswertung erstellt: {pdf_filename}")
        return info_filename
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

def erstelle_auswertungsdiagramme(csv_path: str) -> str:
    """
    Erstellt mehrere Diagramme aus einer beliebigen CSV-Datei und speichert sie als PDF.
    Die Funktion ist robust gegenüber unterschiedlichen CSV-Strukturen.
    """
    # CSV einlesen (Datumsspalte wird, falls vorhanden, als datetime geparst)
    try:
        df = pd.read_csv(csv_path, parse_dates=["datetime"])
    except Exception:
        df = pd.read_csv(csv_path)
    
    pdf_path = os.path.splitext(csv_path)[0] + "_grafik.pdf"
    print("PDF wird gespeichert unter:", pdf_path)
    with PdfPages(pdf_path) as pdf:
        # ========== 1. Korrelationen ===========
        plt.figure(figsize=(10, 8))
        corr = df.corr(numeric_only=True)
        if not corr.empty:
            def custom_fmt(x):
                # 1.0 -> "1", 0.85 -> ".85", -0.85 -> "-.85", 0.00 -> ".00"
                if abs(x) == 1:
                    return "1"
                s = f"{x:.2f}"
                if s.startswith("0"):
                    s = s[1:]
                elif s.startswith("-0"):
                    s = "-" + s[2:]
                return s

            sns.heatmap(
                corr,
                annot=corr.map(custom_fmt),
                cmap="coolwarm",
                fmt="",
                annot_kws={"size": 6},
                cbar_kws={"shrink": 0.8}
            )
            plt.title("Korrelation zwischen numerischen Spalten")
            plt.tight_layout()
            pdf.savefig()
        plt.close()

        # ========== 2. Histogramme für numerische Spalten ===========
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            plt.figure(figsize=(7, 4))
            try:
                sns.histplot(df[col].dropna(), bins=30, kde=True)
                plt.title(f"Histogramm: {col}")
                plt.xlabel(col)
                plt.ylabel("Häufigkeit")
                plt.tight_layout()
                pdf.savefig()
            except Exception as e:
                print(f"Histogramm für {col} konnte nicht erstellt werden: {e}")
            finally:
                plt.close()

        # ========== 3. Boxplots für numerische Spalten ===========
        for col in numeric_cols:
            plt.figure(figsize=(5, 4))
            try:
                sns.boxplot(x=df[col].dropna())
                plt.title(f"Boxplot: {col}")
                plt.xlabel(col)
                plt.tight_layout()
                pdf.savefig()
            except Exception as e:
                print(f"Boxplot für {col} konnte nicht erstellt werden: {e}")
            finally:
                plt.close()

        # ========== 4. Balkendiagramme für kategorische Spalten ===========
        cat_cols = df.select_dtypes(include=['object', 'category']).columns
        for col in cat_cols:
            value_counts = df[col].value_counts().head(10)
            plt.figure(figsize=(8, 4))
            try:
                sns.barplot(x=value_counts.index, y=value_counts.values)
                plt.title(f"Balkendiagramm: Top-Werte in {col}")
                plt.xlabel(col)
                plt.ylabel("Anzahl")
                plt.xticks(rotation=45)
                plt.tight_layout()
                pdf.savefig()
            except Exception as e:
                print(f"Balkendiagramm für {col} konnte nicht erstellt werden: {e}")
            finally:
                plt.close()
        # ========== 4. Tages-Plot: Anzahl Stunden pro Tag ===========
        if "datetime" in df.columns:
            try:
                df["date"] = pd.to_datetime(df["datetime"]).dt.date
                daily_counts = df.groupby("date").size()
                plt.figure(figsize=(15,5))
                daily_counts.plot()
                plt.title("Anzahl Stunden pro Tag (Soll: 24)")
                plt.ylabel("Stunden-Datensätze")
                plt.xlabel("Datum")
                plt.grid(True)
                pdf.savefig()
                plt.close()
                # Fehlende Tage erkennen (Konsolenausgabe)
                missing_days = daily_counts[daily_counts < 24]
                print("Tage mit weniger als 24 Einträgen:", missing_days.count())
                print(missing_days.head())
            except Exception as e:
                print("Tagesplot konnte nicht erstellt werden:", e)
    return pdf_path


# 🚀 SCRIPT VERWENDUNG:
if __name__ == "__main__":
    print("🚀 CSV INFO EXTRACTOR")
    print("="*50)
    
    import sys
    import glob
    download_folder = "C:/Users/Frank/Downloads/"
    csv_files = glob.glob(download_folder + "*.csv")
    if not csv_files:
        print("❌ Keine CSV-Dateien im Download-Ordner gefunden!")
        sys.exit(1)
    print("📂 Gefundene CSV-Dateien im Download-Ordner:")
    for idx, file in enumerate(csv_files, 1):
        print(f"  [{idx}] {os.path.basename(file)}")
    print("\nBitte geben Sie die Nummer der gewünschten Datei ein:")
    while True:
        try:
            auswahl = int(input("Nummer: ").strip())
            if 1 <= auswahl <= len(csv_files):
                csv_file = csv_files[auswahl - 1]
                break
            else:
                print(f"Ungültige Nummer! Bitte eine Zahl zwischen 1 und {len(csv_files)} eingeben.")
        except ValueError:
            print("Ungültige Eingabe! Bitte eine Zahl eingeben.")
    # Script ausführen
    result = csv_info_extractor(csv_file)
    if result:
        print(f"\n🎯 Fertig! Alle Informationen wurden in '{result}' gespeichert.")
        print("\n💡 Das Script kann für jede CSV-Datei verwendet werden:")
        print("   python csv_analyzer_02.py C:/Users/Frank/Downloads/datei.csv")
    else:
        print("\n❌ Analyse konnte nicht abgeschlossen werden.")

