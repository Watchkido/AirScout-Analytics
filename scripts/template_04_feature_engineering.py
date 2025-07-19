import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

def feature_engineering(df):
    # Numerische Features skalieren
    numeric_features = df.select_dtypes(include=['float64', 'int64']).columns
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='mean')),
        ('scaler', StandardScaler())
    ])

    # Kategorische Features kodieren
    categorical_features = df.select_dtypes(include=['object']).columns
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
        ('encoder', OneHotEncoder(handle_unknown='ignore'))
    ])

    # Kombinieren der beiden Transformations-Pipelines
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ]
    )

    # Vorverarbeitungs-Pipeline anwenden
    df_processed = preprocessor.fit_transform(df)
    return df_processed

if __name__ == "__main__":
    # Beispiel: CSV-Datei laden und Features extrahieren
    df = pd.read_csv('path_to_data.csv')
    processed_data = feature_engineering(df)
    print(processed_data)
