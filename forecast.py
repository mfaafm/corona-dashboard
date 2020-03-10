import plotly.graph_objects as go
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import pandas as pd
import numpy as np


def avg_growth_rate(x, days=3):
    growth_rate = x / x.shift(1)
    return np.median(growth_rate[-days:])


def plot_forecast(data, country, num_days):
    confirmed = data.get_country_data(country).loc["Active"]

    if confirmed.shape[0] <= 3:
        return html.H4("Not enough data for forecast.")

    growth_rate = avg_growth_rate(confirmed)
    time_idx = pd.date_range(
        start=confirmed.index[-1] + pd.Timedelta(days=1), periods=num_days, freq="d"
    )
    forecast = np.round(confirmed[-1] * growth_rate ** np.arange(1, num_days))

    fig_data = [
        go.Bar(x=confirmed.index[-7:], y=confirmed[-7:], name="Active"),
        go.Bar(x=time_idx, y=forecast, name="Forecast"),
    ]

    fig = dict(data=fig_data)
    graph = dcc.Graph(figure=fig)
    return [
        dbc.Row(
            [
                dbc.Col(
                    "Exponential forecast based on the number of active cases "
                    f"as of {confirmed.index[-1].strftime('%Y/%m/%d')} using the median "
                    f"growth rate of the last 3 days: {growth_rate:.3f}.",
                    width={"size": 10, "offset": 1},
                )
            ]
        ),
        dbc.Row([dbc.Col(graph)]),
    ]
