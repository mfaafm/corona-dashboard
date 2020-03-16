import logging
import pandas as pd
from datetime import datetime, timedelta


class BMPData(object):
    _url_pattern = (
        "https://interaktiv.morgenpost.de/corona-virus-karte-infektionen-deutschland-weltweit/"
        "data/Coronavirus.{file}.v2.csv?{timestamp}"
    )

    def __init__(self, timeout=30):
        self.logger = logging.getLogger(__name__)
        self.timeout = timedelta(minutes=timeout)
        self.records = ["confirmed", "active", "recovered", "deaths"]
        self.datasets = [
            "timeline",
            "current",
            "history",
            "federal_history",
            "country_history",
            "countries_total",
        ]
        self._maybe_update(force=True)

    @staticmethod
    def get_timestamp():
        ts = datetime.now().timestamp()
        return round(1000 * ts)

    def preprocess(self, df):
        return df.assign(active=df["confirmed"] - df["recovered"] - df["deaths"])

    def load_data(self, which="timeline"):
        url = self._url_pattern.format(file=which, timestamp=self.get_timestamp())
        df = pd.read_csv(url, parse_dates=["date"])
        return self.preprocess(df)

    def get_dataset(self, which="current"):
        if which not in self.datasets:
            raise ValueError(f"Unknown dataset. Must be one of {self.datasets}.")
        self._maybe_update()
        return getattr(self, f"_{which}").copy()

    def get_federal_countries(self):
        self._maybe_update()
        return self._federal_countries.copy()

    def get_country_ranking(self, record="active"):
        self._maybe_update()
        return self._country_ranking[record].copy()

    def get_country_history(self, country="Deutschland"):
        self._maybe_update()
        df = self._countries_history[self._countries_history["country"] == country]
        return df.drop(columns="country").copy()

    def _maybe_update(self, force=False):
        if force or (datetime.utcnow() - self._ts > self.timeout):
            self.logger.info("Data update started")
            self._ts = datetime.utcnow()
            self._timeline = self.load_data("timeline")
            self._current = self.load_data("current")
            self._history = self.load_data("history")
            self._federal_countries = self._get_federal_countries()
            self._federal_history = self._get_federal_history()
            self._countries_history = self._get_countries_history()
            self._countries_total = self._get_countries_total()
            self._country_ranking = self._get_country_ranking()
            self.logger.info("Data update finished")

    def _get_federal_countries(self):
        df = self._history
        parents = pd.Series(df["parent"].unique())
        return parents[parents != "global"].reset_index(drop=True)

    def _get_federal_history(self, country="Deutschland"):
        df = self._history
        country_cols = ["date", "label"] + self.records
        df_ctr = df.loc[df["parent"] == country, country_cols]
        df_ctr = df_ctr.rename(columns={"label": "state"}).reset_index(drop=True)
        return df_ctr.melt(
            id_vars=["state", "date"],
            value_vars=self.records,
            var_name="record",
            value_name="total",
        )

    def _split_parents_and_globals(self, df):
        has_parent = df["parent"].isin(self._federal_countries)
        df_parents = df[has_parent].copy()

        df_globals = df.loc[~has_parent].copy()
        df_globals.drop(columns="parent", inplace=True)
        df_globals.rename(columns={"label": "country"}, inplace=True)
        return df_parents, df_globals

    def _get_countries_history(self):
        df_hist = self._history
        df_parents, df_globals = self._split_parents_and_globals(df_hist)

        df_agg = (
            df_parents.groupby(["parent", "date"])
            .agg({k: "sum" for k in self.records})
            .reset_index()
            .rename(columns=dict(parent="country"))
        )
        df_ctr = pd.concat((df_globals, df_agg), ignore_index=True)

        df = df_ctr.melt(
            id_vars=["country", "date"],
            value_vars=self.records,
            var_name="record",
            value_name="total",
        ).copy()

        df_grouped = df.sort_values(by="date").groupby(["country", "record"])
        df.loc[:, "difference"] = df_grouped["total"].diff()
        df.loc[:, "growth factor"] = df_grouped["total"].apply(lambda s: s / s.shift())
        return df

    def _get_countries_total(self):
        df = self._current
        df_parents, df_globals = self._split_parents_and_globals(df)

        df_agg = df_parents.groupby("parent").agg({k: "sum" for k in self.records})
        df_agg = df_agg.reset_index().rename(columns={"parent": "country"})

        df_total = pd.concat((df_globals, df_agg), ignore_index=True)
        df_total = df_total.reset_index(drop=True)
        return df_total.melt(
            id_vars=["country"],
            value_vars=self.records,
            var_name="record",
            value_name="total",
        )

    def _get_country_ranking(self):
        df = self._countries_total
        return {
            name: group.sort_values(by="total", ascending=False)["country"].to_list()
            for name, group in df.groupby("record")
        }
