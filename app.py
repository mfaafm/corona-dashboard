from dasher import Dasher
from dash.dependencies import Input, Output
from datasource import CSSEData
from timeline import plot_country_timeline
from forecast import plot_forecast

# data refresh rate in minutes
REFRESH_RATE = 30

data = CSSEData(refresh_rate=REFRESH_RATE)

app = Dasher(__name__, title="SARS-CoV-2 dashboard")

app.callback(
    "Timeline",
    _labels=["Country", "Mode", "y-Axis"],
    _layout_kw=dict(widget_cols=3),
    country=data.get_country_ranking(),
    mode=["cumulative", "increase", "growth factor"],
    yaxis=["linear", "log"],
)(lambda *args: plot_country_timeline(data, *args))

app.callback(
    "Forecast",
    _labels=["Country", "Forecast horizon (days)"],
    country=data.get_country_ranking(),
    num_days=(1, 14, 1),
)(lambda *args: plot_forecast(data, *args))


def refresh_countries():
    countries = data.get_country_ranking()
    return [{"label": c, "value": c} for c in countries]


# get country input widgets for timeline & forecast tab
country_input_timeline = app.callbacks["timeline"].widgets[0]
country_input_forecast = app.callbacks["forecast"].widgets[0]

# hack to refresh the list of countries when selecting a country
@app.app.callback(
    Output(country_input_timeline.name, "options"),
    [Input(country_input_timeline.name, country_input_timeline.dependency)],
)
def refresh_countries_timeline(dependency):
    return refresh_countries()


# hack to refresh the list of countries when selecting a country
@app.app.callback(
    Output(country_input_forecast.name, "options"),
    [Input(country_input_forecast.name, country_input_forecast.dependency)],
)
def refresh_countries_forecast(dependency):
    return refresh_countries()


wsgi = app.get_flask_server()

if __name__ == "__main__":
    app.run_server(debug=True)
