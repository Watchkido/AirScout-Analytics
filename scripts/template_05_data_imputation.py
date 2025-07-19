import pandas as pd
from sklearn.impute import SimpleImputer

def impute_missing_values(df):
    # Imputation von fehlenden Werten
    imputer = SimpleImputer(strategy='mean')
    df_imputed = df.copy()
    df_imputed[:] = imputer.fit_transform(df)
    return df_imputed

if __name__ == "__main__":
    # Beispiel: CSV-Datei laden und fehlende Werte imputieren
    df = pd.read_csv('path_to_data.csv')
    df_imputed = impute_missing_values(df)
    print(df_imputed.head())
