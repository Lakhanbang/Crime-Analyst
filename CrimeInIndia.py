import json
import numpy as np
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
import plotly.io as pio

print("Success: All libraries (pandas, dash, plotly) imported correctly!")

pio.renderers.default = 'browser'

# --- Load GeoJSON ---
# --- Load GeoJSON ---
# Using relative paths so the script works on any folder
india_states = json.load(open("states_india (1).geojson", "r"))
state_id_map = {}
for feature in india_states["features"]:
    feature["id"] = feature["properties"]["state_code"]
    state_id_map[feature["properties"]["st_nm"]] = feature["id"]

# --- Load Dataset ---
# --- Load Dataset ---
df_all = pd.read_csv("States10YearsFinal.csv")
df_all["id"] = df_all["State"].apply(lambda x: state_id_map.get(x))

# Detect crime columns (excluding metadata)
crime_columns = [col for col in df_all.columns if col not in ["Year", "State", "id"]]

# --- Create Dash App ---
app = Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H2("Indian Crime Map & State-wise Trends", style={"textAlign": "center"}),

    html.Div([
        html.Div([
            html.Label("Select Crime:"),
            dcc.Dropdown(
                id="crime-dropdown",
                options=[{"label": crime, "value": crime} for crime in crime_columns],
                value="Total Crimes"
            ),
            html.Label("Select Year:"),
            dcc.Slider(
                id="year-slider",
                min=2013,
                max=2022,
                step=1,
                value=2022,
                marks={str(y): str(y) for y in range(2013, 2023)}
            ),
            dcc.Graph(id="crime-map")
        ], style={"width": "55%", "display": "inline-block", "padding": "0 20"}),

        html.Div([
            html.H4("Crime Trend for Selected State"),
            dcc.Graph(id="trend-graph")
        ], style={"width": "43%", "display": "inline-block", "verticalAlign": "top"})
    ])
])

# --- Map Callback ---
@app.callback(
    Output("crime-map", "figure"),
    Input("crime-dropdown", "value"),
    Input("year-slider", "value")
)
def update_map(selected_crime, selected_year):
    df = df_all[df_all["Year"] == selected_year].copy()

    if selected_crime == "Total Crimes":
        df["plot_value"] = df[selected_crime]
        color_scale = "Blues"
    else:
        df["plot_value"] = np.log10(df[selected_crime] + 1)
        color_scale = "Reds"

    fig = px.choropleth(
        df,
        locations="id",
        geojson=india_states,
        color="plot_value",
        hover_name="State",
        hover_data={selected_crime: True, "plot_value": False},
        title=f"{selected_crime} in {selected_year}",
        color_continuous_scale=color_scale
    )

    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(clickmode='event+select')

    return fig

# --- Trend Graph Callback ---
@app.callback(
    Output("trend-graph", "figure"),
    Input("crime-map", "clickData"),
    Input("crime-dropdown", "value")
)
def update_trend_graph(click_data, selected_crime):
    if click_data is None:
        return px.line(title="Click on a state to view its trend")

    state_name = click_data["points"][0]["hovertext"]
    df_state = df_all[df_all["State"] == state_name]

    fig = px.line(
        df_state,
        x="Year",
        y=selected_crime,
        title=f"{selected_crime} Trend in {state_name} (2013–2022)",
        markers=True
    )

    return fig

if __name__ == "__main__":
    app.run(debug=True)
    
    