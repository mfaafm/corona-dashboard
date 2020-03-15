import dash_bootstrap_components as dbc
from dasher import Dasher
from dash.dependencies import Input, Output
from datasource.jhu import JHUData
from dashboard.timeline import plot_country_timeline
from dashboard.forecast import plot_forecast

# data refresh rate in minutes
REFRESH_RATE = 30

data = JHUData(refresh_rate=REFRESH_RATE)

app = Dasher(__name__, title="SARS-CoV-2 dashboard")


# make Germany the default country
countries = data.get_country_ranking()
countries.remove("Germany")
countries.insert(0, "Germany")

app.callback(
    "Timeline",
    _labels=["Country", "Mode", "y-Axis"],
    _layout_kw=dict(widget_cols=3),
    country=countries,
    mode=["total", "difference", "growth factor"],
    yaxis=["linear", "log"],
)(lambda *args: plot_country_timeline(data, *args))

app.callback(
    "Forecast",
    _labels=["Country", "Forecast horizon (days)"],
    country=countries,
    num_days=(1, 7, 1),
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


code_link = dbc.NavLink(
    "source code",
    className="small",
    href="https://github.com/mfaafm/corona-dashboard",
    external_link=True,
)

data_link = dbc.NavLink(
    "data source (JHU CSSE)",
    className="small",
    href="https://github.com/CSSEGISandData/COVID-19",
    external_link=True,
)

# add links to source code and data into navbar
navbar = app.api.layout.navbar
navbar.children.insert(0, code_link)
navbar.children.insert(1, data_link)

wsgi = app.get_flask_server()

if __name__ == "__main__":
    app.run_server(debug=True)
