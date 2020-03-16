import plotly.graph_objects as go
import dash_core_components as dcc
from . import color_map


def _get_growth_rate_figure(df):
    df = df.sort_values("date")
    df["growth factor smooth"] = (
        df.groupby("record")["growth factor"]
        .rolling(3)
        .median()
        .droplevel(level="record")
    )

    raw_data = [
        go.Scatter(
            x=val["date"],
            y=val["growth factor"],
            mode="markers",
            marker=dict(color=color_map[name]),
            name=name,
            visible=True if name == "active" else "legendonly",
        )
        for name, val in df.groupby("record")
    ]
    smooth_data = [
        go.Scatter(
            x=val["date"],
            y=val["growth factor smooth"],
            mode="lines",
            line=dict(color=color_map[name]),
            name=f"{name} (3-day median)",
            hoverinfo="skip",
            visible=True if name == "active" else "legendonly",
        )
        for name, val in df.groupby("record")
    ]
    return raw_data + smooth_data


def plot_country_timeline(data, country, mode, yaxis):
    df = data.get_country_history(country)
    df = df[df["record"] != "confirmed"]

    if mode == "growth factor":
        fig_data = _get_growth_rate_figure(df)
        barmode = None
    else:
        if mode == "difference":
            barmode = "relative"
        else:
            barmode = "stack"

        fig_data = [
            go.Bar(x=val["date"], y=val[mode], name=name, marker_color=color_map[name])
            for name, val in df.groupby("record")
        ]

    layout = go.Layout(barmode=barmode, yaxis=dict(type=yaxis))
    fig = go.Figure(data=fig_data, layout=layout)
    return [dcc.Graph(figure=fig)]
