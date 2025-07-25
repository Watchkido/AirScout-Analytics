from config import CONFIG

import plotly.graph_objects as go
import pandas as pd

df = pd.read_csv("daten.csv")  # Enthält: lat, lon, höhe, temperatur

fig = go.Figure(data=[go.Scatter3d(
    x=df["lon"], y=df["lat"], z=df["höhe"],
    mode='markers',
    marker=dict(
        size=4,
        color=df["temperatur"],  # Farbcodierung nach Temperatur
        colorscale='Viridis',
        opacity=0.8
    )
)])

fig.update_layout(scene=dict(
    xaxis_title='Longitude',
    yaxis_title='Latitude',
    zaxis_title='Höhe'
))

fig.show()
