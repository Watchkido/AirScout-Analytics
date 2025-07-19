import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer

def build_model(df, target_column):
    # Features und Zielvariable trennen
    X = df.drop(target_column, axis=1)
    y = df[target_column]
    
    # Datenaufteilung in Trainings- und Testdaten
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Modell-Pipeline
    model = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='mean')),
        ('scaler', StandardScaler()),
        ('classifier', RandomForestClassifier())
    ])

    # Modell trainieren
    model.fit(X_train, y_train)

    # Vorhersagen
    y_pred = model.predict(X_test)

    # Modellbewertung
    print(classification_report(y_test, y_pred))

if __name__ == "__main__":
    # Beispiel: CSV-Datei laden und Modell aufbauen
    df = pd.read_csv('path_to_data.csv')
    build_model(df, target_column='target')
