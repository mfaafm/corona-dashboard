import pandas as pd
import numpy as np
import plotly.graph_objects as go
import dash_core_components as dcc

EVEN_COLOR = "white"
ODD_COLOR = "aliceblue"


def plot_current(data, sort, ascending):
    df = data.get_dataset("countries_total")

    df_pivot = pd.pivot_table(
        df, index=["country", "date"], columns="record", values="total"
    )
    df_pivot.reset_index(inplace=True)
    df_pivot.sort_values(by=sort, ascending=ascending, inplace=True)
    df_pivot.rename(columns=dict(date="last update"), inplace=True)

    header = [
        f"<b>{c}</b>"
        for c in [
            "Country",
            "Last Update",
            "Confirmed",
            "Active",
            "Recovered",
            "Deaths",
        ]
    ]
    cells = [
        df_pivot["country"],
        df_pivot["last update"].dt.strftime("%d.%m.%Y %H:%M"),
        df_pivot["confirmed"],
        df_pivot["active"],
        df_pivot["recovered"],
        df_pivot["deaths"],
    ]

    fill_color = [
        EVEN_COLOR if x % 2 else ODD_COLOR for x in np.arange(df_pivot.shape[0])
    ]
    table = go.Table(
        header=dict(values=header),
        cells=dict(values=cells, fill_color=[fill_color * 6]),
    )

    fig = dict(data=[table])
    return dcc.Graph(figure=fig)
