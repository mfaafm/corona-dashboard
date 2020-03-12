import plotly.graph_objects as go
import dash_core_components as dcc

PLOTLY_COLORS = ["#1f77b4", "#ff7f0e", "#2ca02c"]


def _get_growth_rate_figure(df):
    df = df / df.shift(1, axis=1)
    df_smooth = df.rolling(3, axis=1).median()

    raw_data = [
        go.Scatter(
            x=val.index,
            y=val,
            mode="markers",
            marker=dict(color=color),
            name=name,
            visible=True if name == "Active" else "legendonly",
        )
        for (name, val), color in zip(df.iterrows(), PLOTLY_COLORS)
        if val.any()
    ]
    smooth_data = [
        go.Scatter(
            x=val.index,
            y=val,
            mode="lines",
            line=dict(color=color),
            name=f"{name} (3-day median)",
            hoverinfo="skip",
            visible=True if name == "Active" else "legendonly",
        )
        for (name, val), color in zip(df_smooth.iterrows(), PLOTLY_COLORS)
        if val.any()
    ]
    return raw_data + smooth_data


def plot_country_timeline(data, country, mode, yaxis):
    show_cols = ["Active", "Deaths", "Recovered"]
    df = data.get_country_data(country).loc[show_cols]

    if mode == "growth factor":
        fig_data = _get_growth_rate_figure(df)
        barmode = None
    else:
        if mode == "difference":
            df = df.diff(axis=1)
            barmode = "relative"
        else:
            barmode = "stack"

        fig_data = [
            go.Bar(x=val.index, y=val, name=name)
            for name, val in df.iterrows()
            if val.any()
        ]

    layout = dict(barmode=barmode, yaxis=dict(type=yaxis))
    fig = dict(data=fig_data, layout=layout)
    return [dcc.Graph(figure=fig)]
