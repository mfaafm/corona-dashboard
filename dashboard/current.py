import plotly.express as px
import dash_core_components as dcc
from . import color_map


def plot_current(data, rank, n):
    df = data.get_dataset("countries_total")
    top_countries = data.get_country_ranking(record=rank)[:n]

    df_top = df[df["country"].isin(top_countries) & (df["record"] != "confirmed")]
    fig = px.bar(
        df_top,
        y="country",
        x="total",
        color="record",
        orientation="h",
        category_orders=dict(country=top_countries),
        color_discrete_map=color_map,
    )
    return dcc.Graph(figure=fig)
