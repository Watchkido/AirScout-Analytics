import folium

def gps_route_auf_karte(csv_path: str, lat_col: str = None, lon_col: str = None, out_path: str = None) -> str:
    """
    Erstellt eine interaktive HTML-Karte mit der GPS-Route aus einer CSV-Datei.
    :param csv_path: Pfad zur CSV-Datei mit GPS-Daten
    :param lat_col: Name der Breitengrad-Spalte (optional, wird sonst automatisch erkannt)
    :param lon_col: Name der Längengrad-Spalte (optional, wird sonst automatisch erkannt)
    :param out_path: Speicherort für die HTML-Karte (optional)
    :return: Pfad zur erzeugten HTML-Datei
    """
    import pandas as pd
    df = pd.read_csv(csv_path)
    # Spalten automatisch erkennen, falls nicht angegeben
    if not lat_col:
        for c in df.columns:
            if c.lower() in ["lat", "latitude", "gps_lat", "gpslatitude"]:
                lat_col = c
                break
    if not lon_col:
        for c in df.columns:
            if c.lower() in ["lon", "lng", "longitude", "gps_lon", "gps_lng", "gpslongitude"]:
                lon_col = c
                break
    if not lat_col or not lon_col:
        raise ValueError("Konnte keine GPS-Spalten erkennen!")
    lat = pd.to_numeric(df[lat_col], errors='coerce')
    lon = pd.to_numeric(df[lon_col], errors='coerce')
    gps_points = list(zip(lat, lon))
    # Mittelpunkt für Karte bestimmen
    center = [lat.mean(), lon.mean()]
    m = folium.Map(location=center, zoom_start=13, tiles="OpenStreetMap")
    folium.PolyLine(gps_points, color="blue", weight=3, opacity=0.7).add_to(m)
    folium.Marker(gps_points[0], tooltip="Start").add_to(m)
    folium.Marker(gps_points[-1], tooltip="Ende").add_to(m)
    if not out_path:
        out_path = csv_path.rsplit('.', 1)[0] + "_route.html"
    m.save(out_path)
    return out_path
from csv_analyser.config import CONFIG 
from typing import List
def amazon_sonderauswertungen(df) -> List[str]:
    """
    Führt Amazon-spezifische und erweiterte Auswertungen durch
    (Umsatz, Top-Kategorien, Zeittrends etc.).
    :param df: DataFrame
    :returns: Liste von Strings für die Info-Datei
    """
    import pandas as pd
    info_content = []
    # 1. Umsätze & Durchschnittswerte
    if all(col in df.columns for col in ['Qty', 'Amount']):
        df_valid = df[df['Qty'] > 0]
        gesamtumsatz = df_valid['Amount'].sum()
        durchschnittspreis = df_valid['Amount'].mean()
        if 'Order ID' in df.columns:
            umsatz_pro_bestellung = (
                df_valid.groupby('Order ID')['Amount'].sum().mean()
            )
        else:
            umsatz_pro_bestellung = None
        info_content.append(
            f"Gesamtumsatz (nur nicht-stornierte Bestellungen): "
            f"{gesamtumsatz:,.2f}"
        )
        info_content.append(
            f"Durchschnittlicher Bestellwert: {durchschnittspreis:,.2f}"
        )
        if umsatz_pro_bestellung is not None:
            info_content.append(
                f"Durchschnittlicher Umsatz pro Bestellung: "
                f"{umsatz_pro_bestellung:,.2f}"
            )
    # 2. Top-Kategorien und Top-SKUs
    if 'Category' in df.columns and 'Qty' in df.columns:
        top_cat = (
            df.groupby('Category')['Qty']
            .sum().sort_values(ascending=False).head(10)
        )
        info_content.append("\nTop 10 Kategorien nach verkaufter Menge:")
        info_content.append(top_cat.to_string())
    if 'SKU' in df.columns and 'Qty' in df.columns:
        top_sku = (
            df.groupby('SKU')['Qty']
            .sum().sort_values(ascending=False).head(10)
        )
        info_content.append("\nTop 10 SKUs nach verkaufter Menge:")
        info_content.append(top_sku.to_string())
    # 3. Zeitliche Trends
    if (
        'Date' in df.columns and 'Qty' in df.columns and 'Amount' in df.columns
    ):
        try:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            trend = (
                df.groupby(df['Date'].dt.to_period('M'))[['Qty', 'Amount']].sum()
            )
            info_content.append("\nMonatliche Trends (Menge & Umsatz):")
            info_content.append(trend.to_string())
        except Exception as e:
            info_content.append(f"Fehler bei Zeittrend-Auswertung: {e}")
    # 4. Geografische Analysen
    if 'ship-city' in df.columns and 'Amount' in df.columns:
        umsatz_stadt = (
            df.groupby('ship-city')['Amount']
            .sum().sort_values(ascending=False).head(10)
        )
        info_content.append("\nTop 10 Städte nach Umsatz:")
        info_content.append(umsatz_stadt.to_string())
    if 'ship-city' in df.columns:
        anzahl_bestellungen = df['ship-city'].value_counts().head(10)
        info_content.append("\nTop 10 Städte nach Bestellanzahl:")
        info_content.append(anzahl_bestellungen.to_string())
    # 5. B2B/B2C Analyse
    if 'B2B' in df.columns and 'Amount' in df.columns:
        b2b_umsatz = df.groupby('B2B')['Amount'].sum()
        info_content.append("\nUmsatz nach B2B/B2C:")
        info_content.append(b2b_umsatz.to_string())
    # 6. Größen-Analyse
    if all(col in df.columns for col in ['Category', 'Size', 'Qty']):
        try:
            size_stat = (
                df.groupby(['Category', 'Size'])['Qty']
                .sum().sort_values(ascending=False).head(10)
            )
            info_content.append("\nTop 10 Größen pro Kategorie:")
            info_content.append(size_stat.to_string())
        except Exception as e:
            info_content.append(f"Fehler bei Größen-Analyse: {e}")
    # 7. Fulfilment-Vergleich
    if 'Fulfilment' in df.columns and 'Amount' in df.columns:
        fulfilment = df.groupby('Fulfilment')['Amount'].sum()
        info_content.append("\nUmsatz nach Fulfilment-Typ:")
        info_content.append(fulfilment.to_string())
    # 8. Fehlende Werte
    missing_summary = df.isnull().sum().sort_values(ascending=False)
    info_content.append("\nFehlende Werte pro Spalte:")
    info_content.append(missing_summary.to_string())
    # 9. Cancelled/Courier Status
    if 'Courier Status' in df.columns and 'Status' in df.columns:
        cancelled_courier = (
            df[df['Courier Status'].isnull()]['Status'].value_counts()
        )
        info_content.append("\nStatus bei fehlendem Courier Status:")
        info_content.append(cancelled_courier.to_string())
    # 10. ASIN → SKU → Style → Kategorie
    if all(
        col in df.columns
        for col in ['ASIN', 'SKU', 'Style', 'Category', 'Qty']
    ):
        asin_sku = (
            df.groupby(['ASIN', 'SKU', 'Style', 'Category'])['Qty']
            .sum().sort_values(ascending=False).head(10)
        )
        info_content.append(
            "\nTop 10 ASIN → SKU → Style → Kategorie nach Menge:"
        )
        info_content.append(asin_sku.to_string())
    # 11. ASINs mit den meisten Rücksendungen oder Stornos (Qty = 0)
    if 'ASIN' in df.columns and 'Qty' in df.columns:
        asin_storno = df[df['Qty'] == 0]['ASIN'].value_counts().head(10)
        info_content.append(
            "\nTop 10 ASINs mit Rücksendungen/Stornos (Qty=0):"
        )
        info_content.append(asin_storno.to_string())
    return info_content
"""
Hilfsfunktionen und gemeinsame Logik für CSV-Analyse-Module.
Erstellt am: 2025-07-21
Autor: Frank Albrecht

Dieses Modul enthält ausgelagerte Funktionen für CSV-Analyse, Statistik und Info-Export.
Alle Funktionen sind nach PEP8 und den Projektvorgaben dokumentiert.
"""

import os
import numpy as np
import pandas as pd
from datetime import datetime
from typing import List, Any

missing_libs = []
ADVANCED_LIBS_AVAILABLE = True

# Erweiterte Bibliotheken robust importieren und global verfügbar machen
try:
    from scipy.stats import zscore
except ImportError:
    zscore = None
    missing_libs.append("scipy")
    ADVANCED_LIBS_AVAILABLE = False

try:
    from sklearn.linear_model import LinearRegression
except ImportError:
    LinearRegression = None
    missing_libs.append("scikit-learn")
    ADVANCED_LIBS_AVAILABLE = False

try:
    import statsmodels.api as sm
except ImportError:
    sm = None
    missing_libs.append("statsmodels")
    ADVANCED_LIBS_AVAILABLE = False


def bibliotheken_check_ausgabe():
    """
    Gibt eine Übersicht über fehlende Bibliotheken für erweiterte Analysen aus.
    :returns: None
    """
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


def lade_csv_robust(csv_filepath: str) -> pd.DataFrame:
    """
    Lädt eine CSV-Datei robust mit verschiedenen Methoden.
    :param csv_filepath: Pfad zur CSV-Datei
    :returns: Geladener DataFrame
    :raises Exception: Wenn keine Methode erfolgreich ist
    """
    try:
        df = pd.read_csv(csv_filepath, sep=',')
        return df
    except pd.errors.ParserError:
        try:
            df = pd.read_csv(csv_filepath)
            return df
        except pd.errors.ParserError:
            try:
                df = pd.read_csv(csv_filepath, sep=';')
                return df
            except pd.errors.ParserError:
                try:
                    df = pd.read_csv(csv_filepath, sep=None, engine='python')
                    return df
                except pd.errors.ParserError:
                    try:
                        df = pd.read_csv(csv_filepath, on_bad_lines='skip')
                        return df
                    except pd.errors.ParserError:
                        raise Exception("CSV-Datei konnte nicht geladen werden")


def erstelle_info_content(df: pd.DataFrame, csv_filepath: str) -> List[str]:
    """
    Erstellt eine vollständige Analyse-Info-Liste für eine CSV-Datei.
    :param df: DataFrame
    :param csv_filepath: Pfad zur CSV-Datei
    :returns: Liste von Strings für die Info-Datei
    """
    info_content = []
    info_content.append("=" * 80)
    filename = os.path.basename(csv_filepath)
    info_content.append(f"CSV ANALYSE REPORT - {filename}")
    timestamp = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
    info_content.append(f"Erstellt am: {timestamp}")
    info_content.append("=" * 80)
    # Grundlegende Infos
    info_content.append(f"\n🔍 1. GRUNDLEGENDE INFORMATIONEN\n{'-'*40}")
    info_content.append(f"📊 Shape: {df.shape[0]} Zeilen × {df.shape[1]} Spalten")
    info_content.append(f"🔢 Gesamt-Datenpunkte: {df.size:,}")
    # Spaltenübersicht
    info_content.append(f"\n📋 2. SPALTEN MIT DATENTYPEN\n{'-'*40}")
    for i, (col, dtype) in enumerate(df.dtypes.items(), 1):
        unique_values = df[col].dropna().unique()
        sample = ', '.join([str(val)[:25] for val in unique_values[:3]])
        info_content.append(f"{i:2d}. {col:<25} → {str(dtype):<12} | Beispiele: {sample if sample else '(keine Werte)'}")
    # Head/Tail
    info_content.append(f"\n👀 3. ERSTE 5 ZEILEN (HEAD)\n{'-'*40}")
    info_content.append(df.head().to_string(max_cols=None, max_colwidth=25))
    info_content.append(f"\n👁️ LETZTE 5 ZEILEN (TAIL)\n{'-'*40}")
    info_content.append(df.tail().to_string(max_cols=None, max_colwidth=25))
    # DataFrame Info
    info_content.append(f"\n📊 4. DATAFRAME INFO\n{'-'*40}")
    info_content.append(f"RangeIndex: {len(df)} entries, 0 to {len(df)-1}")
    info_content.append(f"Data columns (total {len(df.columns)} columns):")
    for i, col in enumerate(df.columns):
        non_null_count = df[col].count()
        dtype = df[col].dtype
        info_content.append(f" {i:2d}  {col:<20} {non_null_count:>6} non-null  {str(dtype)}")
    # Speicherverbrauch
    memory_usage = df.memory_usage(deep=True).sum()
    info_content.append(f"Memory usage: {memory_usage / 1024:.1f} KB")
    # Fehlende Werte
    info_content.append(f"\n❌ 5. NULL VALUES (FEHLENDE WERTE)\n{'-'*40}")
    null_counts = df.isnull().sum()
    total_nulls = null_counts.sum()
    if total_nulls == 0:
        info_content.append("✅ Keine fehlenden Werte gefunden!")
    else:
        info_content.append(f"🚨 Gesamt fehlende Werte: {total_nulls:,}")
        for col, null_count in null_counts.items():
            if null_count > 0:
                info_content.append(f"{col}: {null_count} fehlend ({(null_count/len(df))*100:.1f}%)")
    # Numerische Statistiken
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        info_content.append(f"\n🔢 6. NUMERISCHE STATISTIKEN\n{'-'*40}")
        desc = df[numeric_cols].describe()
        info_content.append(desc.to_string())
    # Kategorische Spalten
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns
    if len(categorical_cols) > 0:
        info_content.append(f"\n📝 7. KATEGORISCHE SPALTEN ANALYSE\n{'-'*40}")
        for col in categorical_cols:
            unique_count = df[col].nunique()
            mode_values = df[col].mode()
            most_common = (mode_values.iloc[0] if len(mode_values) > 0 else "N/A")
            info_content.append(f"{col:<25}: {unique_count:>4} eindeutige Werte, häufigster: '{most_common}'")
    # Duplikate, leere Zeilen, Spalten mit nur einem Wert
    info_content.append(f"\n⭐ 8. ZUSÄTZLICHE INFORMATIONEN\n{'-'*40}")
    duplicate_count = df.duplicated().sum()
    info_content.append(f"🔁 Duplikate: {duplicate_count}")
    empty_rows = df.isnull().all(axis=1).sum()
    info_content.append(f"📭 Komplett leere Zeilen: {empty_rows}")
    single_value_cols = [col for col in df.columns if df[col].nunique() <= 1]
    if single_value_cols:
        info_content.append(f"⚠️  Spalten mit nur einem Wert: {', '.join(single_value_cols)}")
    # Korrelationen
    if len(numeric_cols) > 1:
        info_content.append(f"\n🔗 9. KORRELATIONEN (NUMERISCHE SPALTEN)\n{'-'*40}")
        corr_matrix = df[numeric_cols].corr()
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                if abs(corr_val) > 0.7:
                    col1, col2 = numeric_cols[i], numeric_cols[j]
                    info_content.append(f"🔥 {col1} ↔ {col2}: {corr_val:.3f}")
        if not any(abs(corr_matrix.iloc[i, j]) > 0.7 for i in range(len(corr_matrix.columns)) for j in range(i+1, len(corr_matrix.columns))):
            info_content.append("✅ Keine sehr hohen Korrelationen gefunden")
    return info_content


def advanced_statistics_analysis(df: pd.DataFrame) -> List[str]:
    """
    Führt erweiterte statistische Analysen durch (z.B. Anomalien, Regression, Zeitreihen).
    :param df: DataFrame
    :returns: Liste von Analyse-Strings
    """
    import numpy as np
    try:
        from scipy.stats import zscore, skew, kurtosis
    except ImportError:
        zscore = None
        skew = None
    try:
        from sklearn.linear_model import LinearRegression
    except ImportError:
        LinearRegression = None
    try:
        import statsmodels.api as sm
    except ImportError:
        sm = None


    analysis_results = []
    explanations = {
        'anomalie': "Werte mit |z-score| > 3 gelten als Ausreißer, da sie deutlich vom Mittelwert abweichen. Solche Anomalien können auf Messfehler, Datenprobleme oder besondere Ereignisse hinweisen. Sie sollten genauer geprüft werden, da sie die Analyse beeinflussen können.",
        'verteilung': "Die Schiefe beschreibt, ob die Verteilung symmetrisch oder verzerrt ist. Die Kurtosis gibt an, ob die Verteilung spitz oder flach ist. Diese Maße helfen, die Form der Datenverteilung besser zu verstehen.",
        'regression': "Eine lineare Regression zeigt den Zusammenhang zwischen zwei Variablen. Die Regressionsgleichung und der R²-Wert geben an, wie gut die Daten durch das Modell erklärt werden. Prognosen sind möglich, sollten aber kritisch geprüft werden.",
        'korrelation': "Korrelationen zeigen, wie stark zwei Variablen zusammenhängen. Ein hoher positiver oder negativer Wert weist auf einen engen Zusammenhang hin. Korrelation bedeutet jedoch nicht automatisch Kausalität.",
        'multi_regression': "Eine multiple Regression analysiert den Einfluss mehrerer Variablen auf eine Zielgröße. Die Koeffizienten und p-Werte geben Aufschluss über die Bedeutung der einzelnen Einflussfaktoren. Ein gutes Modell erklärt einen hohen Anteil der Varianz.",
        'zeitreihe': "Zeitreihenanalysen erkennen Trends und Muster über die Zeit. Die Steigung zeigt, ob ein Wert im Zeitverlauf steigt, fällt oder stabil bleibt. Solche Analysen sind wichtig für Prognosen und saisonale Effekte.",
        'optimierung': "Optimierungsempfehlungen basieren auf Korrelationen zwischen Ziel- und Einflussgrößen. Sie zeigen, welche Werte angepasst werden könnten, um das Ziel zu verbessern. Die Empfehlungen sollten immer im Kontext geprüft werden."
    }

    if not ADVANCED_LIBS_AVAILABLE:
        analysis_results.append("⚠️ ERWEITERTE STATISTIKEN NICHT VERFÜGBAR")
        analysis_results.append("📦 Fehlende Bibliotheken:")
        for lib in missing_libs:
            analysis_results.append(f"   ❌ {lib}")
        analysis_results.append("\n🛠️ Installation: pip install " + ' '.join(missing_libs))
        analysis_results.append("🔄 Nach Installation Script erneut ausführen")
        return analysis_results

    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) < 2:
        analysis_results.append("⚠️ Mindestens 2 numerische Spalten für erweiterte Analysen erforderlich")
        return analysis_results

    # 1. FORENSISCHE STATISTIK - Anomalieerkennung
    analysis_results.append("\n🔍 FORENSISCHE STATISTIK - ANOMALIEERKENNUNG")
    analysis_results.append("-" * 50)
    analysis_results.append(explanations['anomalie'])
    from .konstanten import CONFIG
    try:
        for col in numeric_cols[:CONFIG.TOP_N]:
            if df[col].std() > 0 and zscore is not None:
                z_scores = np.abs(zscore(df[col].dropna()))
                outlier_count = (z_scores > CONFIG.OUTLIER_ZSCORE).sum()
                analysis_results.append(f"{col}: {outlier_count} Ausreißer (|z|>{CONFIG.OUTLIER_ZSCORE})")
    except Exception as e:
        analysis_results.append(f"❌ Forensische Analyse fehlgeschlagen: {str(e)}")

    # 2. EXPLORATIVE STATISTIK - Verteilungsanalyse
    analysis_results.append("\n🧭 EXPLORATIVE STATISTIK - VERTEILUNGSANALYSE")
    analysis_results.append("-" * 50)
    analysis_results.append(explanations['verteilung'])
    try:
        for col in numeric_cols[:CONFIG.TOP_N]:
            data = df[col].dropna()
            if len(data) > 0 and skew is not None and kurtosis is not None:
                skewness = skew(data)
                kurt = kurtosis(data)
                if abs(skewness) < CONFIG.SKEW_SYMMETRIC:
                    skew_txt = "symmetrisch"
                elif skewness > CONFIG.SKEW_SYMMETRIC:
                    skew_txt = "rechtsschief"
                else:
                    skew_txt = "linksschief"
                if kurt > CONFIG.KURTOSIS_NORMAL:
                    kurt_txt = "spitz (leptokurtisch)"
                elif kurt < CONFIG.KURTOSIS_NORMAL:
                    kurt_txt = "flach (platykurtisch)"
                else:
                    kurt_txt = "normal (mesokurtisch)"
                analysis_results.append(f"{col}: Schiefe={skewness:.2f} ({skew_txt}), Kurtosis={kurt:.2f} ({kurt_txt})")
    except Exception as e:
        analysis_results.append(f"❌ Explorative Analyse fehlgeschlagen: {str(e)}")

    # 3. PRÄDIKTIVE STATISTIK - Einfache Regression
    analysis_results.append("\n🔮 PRÄDIKTIVE STATISTIK - REGRESSIONSANALYSE")
    analysis_results.append("-" * 50)
    analysis_results.append(explanations['regression'])
    try:
        if len(numeric_cols) >= 2 and LinearRegression is not None:
            X_col = numeric_cols[0]
            y_col = numeric_cols[1]
            valid_data = df[[X_col, y_col]].dropna()
            if len(valid_data) > CONFIG.REGRESSION_MIN_SAMPLES:
                X = valid_data[[X_col]].values
                y = valid_data[y_col].values
                model = LinearRegression()
                model.fit(X, y)
                r_squared = model.score(X, y)
                coef = model.coef_[0]
                analysis_results.append(f"{y_col} = {coef:.3f} * {X_col} + ... (R²={r_squared:.3f})")
    except Exception as e:
        analysis_results.append(f"❌ Prädiktive Analyse fehlgeschlagen: {str(e)}")

    # 4. DIAGNOSTISCHE STATISTIK - Korrelationsanalyse
    analysis_results.append("\n🧠 DIAGNOSTISCHE STATISTIK - KORRELATIONEN")
    analysis_results.append("-" * 50)
    analysis_results.append(explanations['korrelation'])
    try:
        if len(numeric_cols) >= 2:
            corr_matrix = df[numeric_cols].corr()
            high_corr_pairs = []
            for i in range(len(numeric_cols)):
                for j in range(i+1, len(numeric_cols)):
                    corr_val = corr_matrix.iloc[i, j]
                    try:
                        if np.issubdtype(type(corr_val), np.number) and abs(corr_val) > CONFIG.HIGH_CORR:
                            col1, col2 = numeric_cols[i], numeric_cols[j]
                            high_corr_pairs.append((col1, col2, corr_val))
                    except Exception:
                        continue
            if high_corr_pairs:
                for col1, col2, val in high_corr_pairs:
                    analysis_results.append(f"{col1} ↔ {col2}: {val:.3f}")
            else:
                analysis_results.append("✅ Keine sehr hohen Korrelationen gefunden")
    except Exception as e:
        analysis_results.append(f"❌ Diagnostische Analyse fehlgeschlagen: {str(e)}")

    # 5. KAUSALE STATISTIK - Multiple Regression
    analysis_results.append("\n🔄 KAUSALE STATISTIK - REGRESSIONSSTATISTIKEN")
    analysis_results.append("-" * 50)
    analysis_results.append(explanations['multi_regression'])
    try:
        if len(numeric_cols) >= 3 and sm is not None:
            target_col = numeric_cols[0]
            feature_cols = numeric_cols[1:3]
            valid_data = df[numeric_cols[:3]].dropna()
            if len(valid_data) > CONFIG.MULTI_REGRESSION_MIN_SAMPLES:
                X = valid_data[feature_cols]
                y = valid_data[target_col]
                X = sm.add_constant(X)
                model = sm.OLS(y, X).fit()
                analysis_results.append(f"Regressionsstatistik für {target_col} ~ {feature_cols}:")
                analysis_results.append(str(model.summary()))
    except Exception as e:
        analysis_results.append(f"❌ Kausale Analyse fehlgeschlagen: {str(e)}")

    # 6. ZEITREIHENANALYSE (falls Datumsspalte vorhanden)
    analysis_results.append("\n⏳ ZEITREIHENANALYSE")
    analysis_results.append("-" * 50)
    analysis_results.append(explanations['zeitreihe'])
    try:
        date_cols = []
        for col in df.columns:
            if df[col].dtype == 'object' and any(k in col.lower() for k in ['date', 'zeit', 'time', 'stamp', 'tag', 'datum']):
                date_cols.append(col)
        if date_cols and len(numeric_cols) > 0:
            date_col = date_cols[0]
            numeric_col = numeric_cols[0]
            df_temp = df.copy()
            df_temp[date_col] = pd.to_datetime(df_temp[date_col], errors='coerce')
            df_temp = df_temp.dropna(subset=[date_col, numeric_col])
            if len(df_temp) > CONFIG.REGRESSION_MIN_SAMPLES:
                df_temp = df_temp.sort_values(date_col)
                df_temp['time_numeric'] = (df_temp[date_col] - df_temp[date_col].min()).dt.total_seconds() / CONFIG.TIME_DAY_SECONDS
                X = df_temp[['time_numeric']].values
                y = df_temp[numeric_col].values
                if len(X) > 2 and LinearRegression is not None:
                    model = LinearRegression()
                    model.fit(X, y)
                    trend_slope = model.coef_[0]
                    if abs(trend_slope) < CONFIG.TREND_STABLE:
                        trend_direction = "stabil"
                    elif trend_slope > 0:
                        trend_direction = "steigend"
                    else:
                        trend_direction = "fallend"
                    analysis_results.append(f"📈 Trend für {numeric_col}: {trend_direction} (Steigung: {trend_slope:.6f}/Tag)")
                else:
                    analysis_results.append("❌ scikit-learn (LinearRegression) nicht verfügbar für Zeitreihen-Trend")
        else:
            analysis_results.append("📅 Keine Datumsspalten für Zeitreihenanalyse gefunden")
    except Exception as e:
        analysis_results.append(f"❌ Zeitreihenanalyse fehlgeschlagen: {str(e)}")

    # 7. PRÄSKRIPTIVE STATISTIK - Einfache Optimierungsempfehlung
    analysis_results.append("\n🎯 PRÄSKRIPTIVE STATISTIK - OPTIMIERUNGSEMPFEHLUNGEN")
    analysis_results.append("-" * 50)
    analysis_results.append(explanations['optimierung'])
    try:
        if len(numeric_cols) >= 2:
            target_col = numeric_cols[0]
            recommendations = []
            for col in numeric_cols[1:3]:
                corr = df[[target_col, col]].corr().iloc[0, 1]
                try:
                    if np.issubdtype(type(corr), np.number) and abs(corr) > CONFIG.OPTIMIZATION_CORR:
                        if corr > 0:
                            recommendations.append(f"Steigere {col} → {target_col} steigt (Korr={corr:.2f})")
                        else:
                            recommendations.append(f"Reduziere {col} → {target_col} steigt (Korr={corr:.2f})")
                except Exception:
                    continue
            if recommendations:
                analysis_results.extend(recommendations)
            else:
                analysis_results.append("Keine starken Einflussfaktoren gefunden.")
    except Exception as e:
        analysis_results.append(f"❌ Präskriptive Analyse fehlgeschlagen: {str(e)}")

    return analysis_results
    try:
        from sklearn.linear_model import LinearRegression
    except ImportError:
        LinearRegression = None
    try:
        import statsmodels.api as sm
    except ImportError:
        sm = None

    if not ADVANCED_LIBS_AVAILABLE:
        analysis_results.append("⚠️ ERWEITERTE STATISTIKEN NICHT VERFÜGBAR")
        analysis_results.append("📦 Fehlende Bibliotheken:")
        for lib in missing_libs:
            analysis_results.append(f"   ❌ {lib}")
        analysis_results.append("\n🛠️ Installation: pip install " + ' '.join(missing_libs))
        analysis_results.append("🔄 Nach Installation Script erneut ausführen")
        return analysis_results

    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) < 2:
        analysis_results.append("⚠️ Mindestens 2 numerische Spalten für erweiterte Analysen erforderlich")
        return analysis_results

    # 1. FORENSISCHE STATISTIK - Anomalieerkennung
    analysis_results.append("\n🔍 FORENSISCHE STATISTIK - ANOMALIEERKENNUNG")
    analysis_results.append("-" * 50)
    analysis_results.append(explanations['anomalie'])
    try:
        for col in numeric_cols[:3]:
            if df[col].std() > 0 and zscore is not None:
                z_scores = np.abs(zscore(df[col].dropna()))
                outlier_count = (z_scores > 3).sum()
                analysis_results.append(f"{col}: {outlier_count} Ausreißer (|z|>3)")
    except Exception as e:
        analysis_results.append(f"❌ Forensische Analyse fehlgeschlagen: {str(e)}")

    # 2. EXPLORATIVE STATISTIK - Verteilungsanalyse
    analysis_results.append("\n🧭 EXPLORATIVE STATISTIK - VERTEILUNGSANALYSE")
    analysis_results.append("-" * 50)
    analysis_results.append(explanations['verteilung'])
    try:
        for col in numeric_cols[:3]:
            data = df[col].dropna()
            if len(data) > 0 and skew is not None and kurtosis is not None:
                skewness = skew(data)
                kurt = kurtosis(data)
                if abs(skewness) < 0.5:
                    skew_txt = "symmetrisch"
                elif skewness > 0.5:
                    skew_txt = "rechtsschief"
                else:
                    skew_txt = "linksschief"
                if kurt > 3:
                    kurt_txt = "spitz (leptokurtisch)"
                elif kurt < 3:
                    kurt_txt = "flach (platykurtisch)"
                else:
                    kurt_txt = "normal (mesokurtisch)"
                analysis_results.append(f"{col}: Schiefe={skewness:.2f} ({skew_txt}), Kurtosis={kurt:.2f} ({kurt_txt})")
    except Exception as e:
        analysis_results.append(f"❌ Explorative Analyse fehlgeschlagen: {str(e)}")

    # 3. PRÄDIKTIVE STATISTIK - Einfache Regression
    analysis_results.append("\n� PRÄDIKTIVE STATISTIK - REGRESSIONSANALYSE")
    analysis_results.append("-" * 50)
    analysis_results.append(explanations['regression'])
    try:
        if len(numeric_cols) >= 2 and LinearRegression is not None:
            X_col = numeric_cols[0]
            y_col = numeric_cols[1]
            valid_data = df[[X_col, y_col]].dropna()
            if len(valid_data) > 5:
                X = valid_data[[X_col]].values
                y = valid_data[y_col].values
                model = LinearRegression()
                model.fit(X, y)
                r_squared = model.score(X, y)
                coef = model.coef_[0]
                analysis_results.append(f"{y_col} = {coef:.3f} * {X_col} + ... (R²={r_squared:.3f})")
    except Exception as e:
        analysis_results.append(f"❌ Prädiktive Analyse fehlgeschlagen: {str(e)}")

    # 4. DIAGNOSTISCHE STATISTIK - Korrelationsanalyse
    analysis_results.append("\n🧠 DIAGNOSTISCHE STATISTIK - KORRELATIONEN")
    analysis_results.append("-" * 50)
    analysis_results.append(explanations['korrelation'])
    try:
        if len(numeric_cols) >= 2:
            corr_matrix = df[numeric_cols].corr()
            high_corr_pairs = []
            for i in range(len(numeric_cols)):
                for j in range(i+1, len(numeric_cols)):
                    corr_val = corr_matrix.iloc[i, j]
                    try:
                        if np.issubdtype(type(corr_val), np.number) and abs(corr_val) > 0.7:
                            col1, col2 = numeric_cols[i], numeric_cols[j]
                            high_corr_pairs.append((col1, col2, corr_val))
                    except Exception:
                        continue
            if high_corr_pairs:
                for col1, col2, val in high_corr_pairs:
                    analysis_results.append(f"{col1} ↔ {col2}: {val:.3f}")
            else:
                analysis_results.append("✅ Keine sehr hohen Korrelationen gefunden")
    except Exception as e:
        analysis_results.append(f"❌ Diagnostische Analyse fehlgeschlagen: {str(e)}")

    # 5. KAUSALE STATISTIK - Multiple Regression
    analysis_results.append("\n🔄 KAUSALE STATISTIK - REGRESSIONSSTATISTIKEN")
    analysis_results.append("-" * 50)
    analysis_results.append(explanations['multi_regression'])
    try:
        if len(numeric_cols) >= 3 and sm is not None:
            target_col = numeric_cols[0]
            feature_cols = numeric_cols[1:3]
            valid_data = df[numeric_cols[:3]].dropna()
            if len(valid_data) > 10:
                X = valid_data[feature_cols]
                y = valid_data[target_col]
                X = sm.add_constant(X)
                model = sm.OLS(y, X).fit()
                analysis_results.append(f"Regressionsstatistik für {target_col} ~ {feature_cols}:")
                analysis_results.append(str(model.summary()))
    except Exception as e:
        analysis_results.append(f"❌ Kausale Analyse fehlgeschlagen: {str(e)}")

    # 6. ZEITREIHENANALYSE (falls Datumsspalte vorhanden)
    analysis_results.append("\n⏳ ZEITREIHENANALYSE")
    analysis_results.append("-" * 50)
    analysis_results.append(explanations['zeitreihe'])
    try:
        date_cols = []
        for col in df.columns:
            if df[col].dtype == 'object' and any(k in col.lower() for k in ['date', 'zeit', 'time', 'stamp', 'tag', 'datum']):
                date_cols.append(col)
        if date_cols and len(numeric_cols) > 0:
            date_col = date_cols[0]
            numeric_col = numeric_cols[0]
            df_temp = df.copy()
            df_temp[date_col] = pd.to_datetime(df_temp[date_col], errors='coerce')
            df_temp = df_temp.dropna(subset=[date_col, numeric_col])
            if len(df_temp) > 5:
                df_temp = df_temp.sort_values(date_col)
                df_temp['time_numeric'] = (df_temp[date_col] - df_temp[date_col].min()).dt.total_seconds() / 86400.0
                X = df_temp[['time_numeric']].values
                y = df_temp[numeric_col].values
                if len(X) > 2 and LinearRegression is not None:
                    model = LinearRegression()
                    model.fit(X, y)
                    trend_slope = model.coef_[0]
                    if abs(trend_slope) < 0.001:
                        trend_direction = "stabil"
                    elif trend_slope > 0:
                        trend_direction = "steigend"
                    else:
                        trend_direction = "fallend"
                    analysis_results.append(f"📈 Trend für {numeric_col}: {trend_direction} (Steigung: {trend_slope:.6f}/Tag)")
                else:
                    analysis_results.append("❌ scikit-learn (LinearRegression) nicht verfügbar für Zeitreihen-Trend")
        else:
            analysis_results.append("📅 Keine Datumsspalten für Zeitreihenanalyse gefunden")
    except Exception as e:
        analysis_results.append(f"❌ Zeitreihenanalyse fehlgeschlagen: {str(e)}")

    # 7. PRÄSKRIPTIVE STATISTIK - Einfache Optimierungsempfehlung
    analysis_results.append("\n🎯 PRÄSKRIPTIVE STATISTIK - OPTIMIERUNGSEMPFEHLUNGEN")
    analysis_results.append("-" * 50)
    analysis_results.append(explanations['optimierung'])
    try:
        if len(numeric_cols) >= 2:
            target_col = numeric_cols[0]
            recommendations = []
            for col in numeric_cols[1:3]:
                corr = df[[target_col, col]].corr().iloc[0, 1]
                try:
                    if np.issubdtype(type(corr), np.number) and abs(corr) > 0.5:
                        if corr > 0:
                            recommendations.append(f"Steigere {col} → {target_col} steigt (Korr={corr:.2f})")
                        else:
                            recommendations.append(f"Reduziere {col} → {target_col} steigt (Korr={corr:.2f})")
                except Exception:
                    continue
            if recommendations:
                analysis_results.extend(recommendations)
            else:
                analysis_results.append("Keine starken Einflussfaktoren gefunden.")
    except Exception as e:
        analysis_results.append(f"❌ Präskriptive Analyse fehlgeschlagen: {str(e)}")

    return analysis_results

    if len(numeric_cols) < 2:
        analysis_results.append(
            "⚠️ Mindestens 2 numerische Spalten für erweiterte Analysen erforderlich"
        )
        return analysis_results

    # 1. FORENSISCHE STATISTIK - Anomalieerkennung
    analysis_results.append("\n🔍 FORENSISCHE STATISTIK - ANOMALIEERKENNUNG")
    analysis_results.append("-" * 50)
    analysis_results.append(explanations['anomalie'])
    try:
        for col in numeric_cols[:3]:
            if df[col].std() > 0:
                if 'zscore' in globals() and zscore is not None:
                    z_scores = np.abs(zscore(df[col].dropna()))
                    anomalies = np.sum(z_scores > 3)
                    if anomalies > 0:
                        anomaly_percentage = (anomalies / len(df)) * 100
                        analysis_results.append(
                            f"🚨 {col}: {anomalies} Anomalien "
                            f"({anomaly_percentage:.1f}%) mit |z-score| > 3"
                        )
                    else:
                        analysis_results.append(
                            f"✅ {col}: Keine Anomalien gefunden"
                        )
                else:
                    analysis_results.append("❌ scipy (zscore) nicht verfügbar für Anomalieerkennung")
    except Exception as e:
        analysis_results.append(f"❌ Forensische Analyse fehlgeschlagen: {str(e)}")

    # 2. EXPLORATIVE STATISTIK - Verteilungsanalyse
    analysis_results.append("\n🧭 EXPLORATIVE STATISTIK - VERTEILUNGSANALYSE")
    analysis_results.append("-" * 50)
    analysis_results.append(explanations['verteilung'])
    try:
        for col in numeric_cols[:3]:
            data = df[col].dropna()
            if len(data) > 0:
                skewness = data.skew()
                kurtosis = data.kurtosis()
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
        analysis_results.append(
            f"❌ Explorative Analyse fehlgeschlagen: {str(e)}"
        )

    # 3. PRÄDIKTIVE STATISTIK - Einfache Regression
    analysis_results.append("\n🔮 PRÄDIKTIVE STATISTIK - REGRESSIONSANALYSE")
    analysis_results.append("-" * 50)
    analysis_results.append(explanations['regression'])
    try:
        if len(numeric_cols) >= 2:
            X_col = numeric_cols[0]
            y_col = numeric_cols[1]
            valid_data = df[[X_col, y_col]].dropna()
            if len(valid_data) > 5:
                X = valid_data[[X_col]].values
                y = valid_data[y_col].values
                if 'LinearRegression' in globals() and LinearRegression is not None:
                    model = LinearRegression()
                    model.fit(X, y)
                    r_squared = model.score(X, y)
                    coef = model.coef_[0]
                    intercept = model.intercept_
                    analysis_results.append(
                        f"📈 {y_col} = {intercept:.3f} + {coef:.3f} × {X_col}"
                    )
                    analysis_results.append(
                        f"📊 R² = {r_squared:.3f} (Erklärte Varianz: {r_squared*100:.1f}%)"
                    )
                    mean_x = X.mean()
                    prediction = model.predict(np.array([[mean_x]]))[0]
                    analysis_results.append(
                        f"🎯 Prognose für {X_col}={mean_x:.2f}: {y_col}={prediction:.2f}"
                    )
                else:
                    analysis_results.append("❌ scikit-learn (LinearRegression) nicht verfügbar für Regression")
            else:
                analysis_results.append("⚠️ Zu wenige Datenpunkte für Regression")
    except Exception as e:
        analysis_results.append(f"❌ Prädiktive Analyse fehlgeschlagen: {str(e)}")

    # 4. DIAGNOSTISCHE STATISTIK - Korrelationsanalyse
    analysis_results.append("\n🧠 DIAGNOSTISCHE STATISTIK - KORRELATIONEN")
    analysis_results.append("-" * 50)
    analysis_results.append(explanations['korrelation'])
    try:
        if len(numeric_cols) >= 2:
            corr_matrix = df[numeric_cols].corr()
            high_corr_pairs = []
            for i in range(len(numeric_cols)):
                for j in range(i+1, len(numeric_cols)):
                    corr_val = corr_matrix.iloc[i, j]
                    if abs(corr_val) > 0.5:
                        high_corr_pairs.append(
                            f"{numeric_cols[i]} ↔ {numeric_cols[j]}: r={corr_val:.3f}"
                        )
            if high_corr_pairs:
                analysis_results.extend(high_corr_pairs[:5])
            else:
                analysis_results.append("📊 Keine starken Korrelationen (|r| > 0.5) gefunden")
    except Exception as e:
        analysis_results.append(f"❌ Diagnostische Analyse fehlgeschlagen: {str(e)}")

    # 5. KAUSALE STATISTIK - Regressionsmodell mit Statistiken
    analysis_results.append("\n🔄 KAUSALE STATISTIK - REGRESSIONSSTATISTIKEN")
    analysis_results.append("-" * 50)
    analysis_results.append(explanations['multi_regression'])
    try:
        if len(numeric_cols) >= 3:
            target_col = numeric_cols[0]
            feature_cols = numeric_cols[1:3]
            valid_data = df[numeric_cols[:3]].dropna()
            if len(valid_data) > 10:
                X = valid_data[feature_cols]
                y = valid_data[target_col]
                if 'LinearRegression' in globals() and LinearRegression is not None:
                    model = LinearRegression()
                    model.fit(X, y)
                    r_squared = model.score(X, y)
                    analysis_results.append(
                        f"📈 {target_col} ~ {feature_cols[0]} + {feature_cols[1]}: R²={r_squared:.3f}"
                    )
                else:
                    analysis_results.append("❌ scikit-learn (LinearRegression) nicht verfügbar für multiple Regression")
            else:
                analysis_results.append("⚠️ Zu wenige Datenpunkte für multiple Regression")
    except Exception as e:
        analysis_results.append(f"❌ Kausale Analyse fehlgeschlagen: {str(e)}")

    # 6. ZEITREIHENANALYSE (falls Datumsspalte vorhanden)
    analysis_results.append("\n⏳ ZEITREIHENANALYSE")
    analysis_results.append("-" * 50)
    analysis_results.append(explanations['zeitreihe'])
    try:
        date_cols = [col for col in df.columns if any(kw in col.lower() for kw in ["date", "zeit", "time", "stamp", "tag", "datum"])]
        if date_cols and len(numeric_cols) > 0:
            date_col = date_cols[0]
            numeric_col = numeric_cols[0]
            df_temp = df.copy()
            df_temp[date_col] = pd.to_datetime(df_temp[date_col], errors='coerce')
            df_temp = df_temp.dropna(subset=[date_col, numeric_col])
            if len(df_temp) > 5:
                df_temp = df_temp.sort_values(date_col)
                df_temp['time_numeric'] = (df_temp[date_col] - df_temp[date_col].min()).dt.days
                X = df_temp[['time_numeric']].values
                y = df_temp[numeric_col].values
                if len(X) > 2 and 'LinearRegression' in globals() and LinearRegression is not None:
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
                        f"📈 Trend für {numeric_col}: {trend_direction} (Steigung: {trend_slope:.6f}/Tag)"
                    )
                else:
                    analysis_results.append("❌ scikit-learn (LinearRegression) nicht verfügbar für Zeitreihen-Trend")
            else:
                analysis_results.append("⚠️ Zu wenige Datenpunkte für Zeitreihenanalyse")
        else:
            analysis_results.append("📅 Keine Datumsspalten für Zeitreihenanalyse gefunden")
    except Exception as e:
        analysis_results.append(f"❌ Zeitreihenanalyse fehlgeschlagen: {str(e)}")

    # 7. PRÄSKRIPTIVE STATISTIK - Einfache Optimierungsempfehlung
    analysis_results.append("\n🎯 PRÄSKRIPTIVE STATISTIK - OPTIMIERUNGSEMPFEHLUNGEN")
    analysis_results.append("-" * 50)
    analysis_results.append(explanations['optimierung'])
    try:
        if len(numeric_cols) >= 2:
            target_col = numeric_cols[0]
            recommendations = []
            for col in numeric_cols[1:3]:
                corr = df[[target_col, col]].corr().iloc[0, 1]
                if abs(corr) > 0.5:
                    if corr > 0:
                        recommendations.append(
                            f"🔼 Erhöhe {col} → {target_col} steigt (Korr={corr:.2f})"
                        )
                    else:
                        recommendations.append(
                            f"🔽 Senke {col} → {target_col} steigt (Korr={corr:.2f})"
                        )
            if recommendations:
                analysis_results.extend(recommendations)
            else:
                analysis_results.append("ℹ️ Keine starken Einflussfaktoren für Optimierung gefunden")
    except Exception as e:
        analysis_results.append(f"❌ Präskriptive Analyse fehlgeschlagen: {str(e)}")

    return analysis_results


def gps_auswertung(df: pd.DataFrame) -> List[str]:
    """
    Führt eine spezielle GPS-Auswertung durch: Streckenberechnung, Geschwindigkeit, Heatmap.
    :param df: DataFrame mit GPS-Daten (Spalten: lat, lon, ggf. Zeit)
    :returns: Liste von Analyse-Strings
    """
    ergebnisse = []
    # Prüfe auf notwendige Spalten
    lat_col = None
    lon_col = None
    zeit_col = None
    for col in df.columns:
        if col.lower() in ["lat", "latitude"]:
            lat_col = col
        if col.lower() in ["lon", "lng", "longitude"]:
            lon_col = col
        if col.lower() in ["zeit", "time", "timestamp", "datetime"]:
            zeit_col = col
    if not lat_col or not lon_col:
        ergebnisse.append("❌ Keine GPS-Koordinaten gefunden (lat/lon)")
        return ergebnisse
    # Haversine-Funktion
    def haversine(lat1, lon1, lat2, lon2):
        from math import radians, sin, cos, sqrt, atan2
        R = 6371.0  # Erdradius in km
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return R * c
    # Streckenberechnung
    lat = np.asarray(df[lat_col].astype(float).values)
    lon = np.asarray(df[lon_col].astype(float).values)
    strecke_km = 0.0
    for i in range(1, len(lat)):
        strecke_km += haversine(lat[i-1], lon[i-1], lat[i], lon[i])
    ergebnisse.append(f"🗺️ Gesamte Strecke: {strecke_km:.3f} km")
    # Geschwindigkeit (falls Zeit vorhanden)
    v_avg = None
    zeit = None
    if zeit_col:
        try:
            zeit = pd.to_datetime(df[zeit_col])
            zeit = np.asarray(zeit)
            zeiten_s = (zeit - zeit[0]) / np.timedelta64(1, 's')
            gesamtzeit_h = (zeiten_s[-1] - zeiten_s[0]) / 3600 if len(zeiten_s) > 1 else 0
            if gesamtzeit_h > 0:
                v_avg = strecke_km / gesamtzeit_h
                ergebnisse.append(f"🚗 Durchschnittsgeschwindigkeit: {v_avg:.2f} km/h")
            else:
                ergebnisse.append("⚠️ Zeitspanne zu kurz oder nur ein Zeitwert")
        except Exception as e:
            ergebnisse.append(f"⚠️ Zeitspalte konnte nicht ausgewertet werden: {e}")
    else:
        ergebnisse.append("ℹ️ Keine Zeitspalte für Geschwindigkeitsberechnung gefunden")

    # Visualisierungen erzeugen
    import matplotlib.pyplot as plt
    import os
    base = "gps_viz"
    pfad = os.path.dirname(df.attrs.get('source_path', '')) or os.getcwd()
    # 1. Streckenkarte
    strecken_png = os.path.join(pfad, f"{base}_strecke.png")
    plt.figure(figsize=(8, 6))
    plt.plot(lon, lat, marker="o", markersize=2, linewidth=1, color="blue")
    plt.title("GPS-Route (Karte)")
    plt.xlabel("Längengrad")
    plt.ylabel("Breitengrad")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(strecken_png)
    plt.close()
    ergebnisse.append(f"🗺️ Streckenkarte gespeichert: {strecken_png}")

    # 2. Höhenprofil (falls Höhe vorhanden)
    hoehe_col = None
    for col in df.columns:
        if col.lower() in ["hoehe", "höhe", "elevation", "altitude"]:
            hoehe_col = col
            break
    if hoehe_col is not None:
        hoehe = np.asarray(df[hoehe_col].astype(float).values)
        plt.figure(figsize=(10, 4))
        if zeit is not None:
            plt.plot(zeit, hoehe, color="green")
            plt.xlabel("Zeit")
        else:
            plt.plot(np.arange(len(hoehe)), hoehe, color="green")
            plt.xlabel("Messpunkt")
        plt.ylabel("Höhe (m)")
        plt.title("Höhenprofil")
        plt.grid(True)
        plt.tight_layout()
        hoehe_png = os.path.join(pfad, f"{base}_hoehenprofil.png")
        plt.savefig(hoehe_png)
        plt.close()
        ergebnisse.append(f"⛰️ Höhenprofil gespeichert: {hoehe_png}")
    else:
        ergebnisse.append("ℹ️ Keine Höhenangaben für Höhenprofil gefunden")

    # 3. Heatmap der GPS-Punkte
    try:
        import seaborn as sns
        plt.figure(figsize=(8, 6))
        sns.kdeplot(x=lon, y=lat, cmap="Reds", fill=True, bw_adjust=0.2, thresh=0.05)
        plt.title("Heatmap der GPS-Punkte")
        plt.xlabel("Längengrad")
        plt.ylabel("Breitengrad")
        plt.tight_layout()
        heatmap_png = os.path.join(pfad, f"{base}_heatmap.png")
        plt.savefig(heatmap_png)
        plt.close()
        ergebnisse.append(f"🌡️ Heatmap gespeichert: {heatmap_png}")
    except Exception as e:
        ergebnisse.append(f"⚠️ Heatmap konnte nicht erzeugt werden: {e}")

    return ergebnisse
