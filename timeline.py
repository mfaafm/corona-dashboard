import plotly.graph_objects as go
import dash_core_components as dcc


def plot_country_timeline(data, country, mode, yaxis):
    show_cols = ["Active", "Deaths", "Recovered"]
    df = data.get_country_data(country).loc[show_cols]

    if mode == "difference":
        df = df.diff(axis=1)
        barmode = "stack"
    elif mode == "growth factor":
        df = df / df.shift(1, axis=1)
        barmode = "group"
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
