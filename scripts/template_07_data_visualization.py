import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def visualize_data(df):
    # Scatterplot
    sns.pairplot(df)
    plt.show()

    # Boxplot für jede Kategorie
    for column in df.select_dtypes(include=['object']).columns:
        plt.figure(figsize=(10, 6))
        sns.boxplot(x=column, y='target', data=df)
        plt.show()

    # Heatmap der Korrelationen
    plt.figure(figsize=(10, 6))
    corr_matrix = df.corr()
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5)
    plt.show()

if __name__ == "__main__":
    # Beispiel: CSV-Datei laden und visualisieren
    df = pd.read_csv('path_to_data.csv')
    visualize_data(df)
