import plotly.graph_objects as go
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import pandas as pd
import numpy as np
from . import colors


def avg_growth_rate(x, days=3):
    growth_rate = x / x.shift(1)
    return np.median(growth_rate[-days:])


def plot_forecast(data, country, num_days=3):
    active = data.get_country_history(country)
    active = active[active.record == "active"].drop(columns="record")

    if active.shape[0] <= 3:
        return html.H4("Not enough data for forecast.")

    growth_rate = avg_growth_rate(active["total"])
    time_idx = pd.date_range(
        start=active["date"].iloc[-1] + pd.Timedelta(days=1), periods=num_days, freq="d"
    )

    x0 = active["total"].iloc[-1]
    forecast = np.round(x0 * growth_rate ** np.arange(1, num_days + 1))

    fig_data = [
        go.Bar(x=active["date"].iloc[-7:], y=active["total"].iloc[-7:], name="active", marker_color=colors[0]),
        go.Bar(x=time_idx, y=forecast, name="forecast", marker_color=colors[1]),
    ]

    fig = dict(data=fig_data)
    graph = dcc.Graph(figure=fig)
    return [
        dbc.Row(
            [
                dbc.Col(
                    "Exponential forecast based on the number of active cases "
                    f"as of {active['date'].iloc[-1].strftime('%Y/%m/%d')} using the median "
                    f"growth rate of the last 3 days: {growth_rate:.3f}.",
                    width={"size": 10, "offset": 1},
                )
            ]
        ),
        dbc.Row([dbc.Col(graph)]),
    ]
