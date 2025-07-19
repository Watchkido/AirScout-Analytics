from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import pandas as pd

def evaluate_model(y_true, y_pred):
    # Klassifikationsbericht
    print("Klassifikationsbericht:")
    print(classification_report(y_true, y_pred))
    
    # Confusion Matrix
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_true, y_pred))
    
    # ROC-AUC (für binäre Klassifikation)
    print("\nROC-AUC:")
    print(roc_auc_score(y_true, y_pred))

if __name__ == "__main__":
    # Beispiel: Wahrheitswerte und Vorhersagen für die Evaluierung
    y_true = pd.Series([0, 1, 0, 1, 0])
    y_pred = pd.Series([0, 1, 0, 0, 1])
    evaluate_model(y_true, y_pred)
        
