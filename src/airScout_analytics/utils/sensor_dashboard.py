import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

# Lade die CSV-Datei
csv_path = r"E:\dev\projekt_python_venv\data\data\ergebnisse\2025_07_21_04_50\bearbeitet3\feature_2025_07_21_04_50_umgerechnet_ema.csv"
df = pd.read_csv(csv_path)

# Zeitformatierung (optional)
df['DateTime'] = pd.to_datetime(df['DateTime'])

# App-Start
app = Dash(__name__)
app.title = "Sensor Dashboard"

# MQ2  (Flüssiggas (LPG), i-Butan, Propan, Methan, Wasserstoff, Alkohol, Rauch - 100 bis 10000ppm): A0 [MQ2]
# MQ3  (Alkohol, Ethanol - 100 bis 10000ppm): A1 [MQ3]
# MQ4  (Methan, CNG, Erdgas, LNG - 200 bis 10000ppm, keine Alkohol-/Koch-/Zigarettenrauch): A2 [MQ4]
# MQ5  (Erdgas, LPG, LNG, iso-Butan, Propan, Stadtgas - 200 bis 10000ppm): A3 [MQ5]
# MQ6  (Flüssiggas wie Butan, Propan, Methan, brennbare Gase - 300 bis 10000ppm): A4 [MQ6]
# MQ7  (Kohlenmonoxid CO - 10 bis 1000ppm CO, 100 bis 10000ppm brennbare Gase): A5 [MQ7]
# MQ8  (Wasserstoff H2, wasserstoffhaltige Gase - 100 bis 1000ppm): A6 [MQ8]
# MQ9  (CO, entflammbare Gase - 0 bis 2000ppm CO, 500 bis 10000ppm CH4, 500 bis 10000ppm Flüssiggas): A7 [MQ9]
sensor_gas_info = {
    'MQ2': 'Flüssiggas, Butan, Propan, Methan, Wasserstoff, Alkohol, Rauch',
    'MQ3': 'Alkohol, Ethanol',
    'MQ4': 'Methan, Erdgas, LNG',
    'MQ5': 'Erdgas, LPG, LNG, iso-Butan, Propan, Stadtgas',
    'MQ6': 'Flüssiggas, Butan, Propan, Methan, brennbare Gase',
    'MQ7': 'Kohlenmonoxid, brennbare Gase',
    'MQ8': 'Wasserstoff, wasserstoffhaltige Gase',
    'MQ9': 'Kohlenmonoxid, Methan, Flüssiggas'
}
sensor_options = [
    'Temperature_DHT_C', 'Humidity_RH', 'Light_Level', 'Radiation_CPS',
    'MQ2', 'MQ3', 'MQ4', 'MQ5', 'MQ6', 'MQ7', 'MQ8', 'MQ9', 'MQ135'
]

app.layout = html.Div([
    html.H1("📈 Sensor Dashboard"),
    html.Label("Wähle Sensor:"),
    dcc.Dropdown(
        id='sensor-dropdown',
        options=[{'label': s, 'value': s} for s in sensor_options],
        value='Temperature_DHT_C'
    ),
    html.Div([
        html.Div([
            dcc.Graph(id='sensor-graph')
        ], style={"flex": "1", "margin-right": "10px"}),
        html.Div([
            dcc.Graph(id='gps-map')
        ], style={"flex": "1", "margin-left": "10px"})
    ], style={"display": "flex", "flex-direction": "row", "gap": "20px"}),
    html.Hr(),
])


@app.callback(
    Output('sensor-graph', 'figure'),
    Output('gps-map', 'figure'),
    Input('sensor-dropdown', 'value')
)
def update_graph(sensor):
    # Gas-Info für Titel
    gas_info = sensor_gas_info.get(sensor, "")
    if gas_info:
        title_line = f"{sensor} ({gas_info}) über Zeit"
        title_map = f"{sensor} ({gas_info}) auf Karte"
    else:
        title_line = f"{sensor} über Zeit"
        title_map = f"{sensor} auf Karte"

    fig_line = px.line(df, x='DateTime', y=sensor, title=title_line, height=1000)

    # GPS Map mit Sensorfarbe
    if 'GPS_Lat' in df.columns and 'GPS_Lon' in df.columns:
        fig_map = px.scatter_mapbox(
            df, lat="GPS_Lat", lon="GPS_Lon", color=sensor,
            hover_data=["DateTime"],
            zoom=12, height=800, title=title_map
        )
        fig_map.update_layout(mapbox_style="open-street-map")
    else:
        fig_map = {}

    return fig_line, fig_map


if __name__ == '__main__':
    app.run(debug=True)
