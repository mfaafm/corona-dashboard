import pandas as pd
from datetime import datetime, timedelta


class CSSEData(object):
    url_pattern = (
        "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/"
        "csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-{}.csv"
    )
    meta_cols = ["Province/State", "Country/Region", "Lat", "Long", "Record"]

    def __init__(self, refresh_rate=15):
        self.refresh_rate = refresh_rate
        self.data_sources = {
            r: self.url_pattern.format(r) for r in ["Confirmed", "Deaths", "Recovered"]
        }
        self.auto_refresh(force=True)

    def load_data(self):
        df_list = [
            pd.read_csv(data).assign(Record=record)
            for record, data in self.data_sources.items()
        ]
        df = pd.concat(df_list, ignore_index=True)

        df.rename(
            columns=lambda c: pd.to_datetime(c) if c not in self.meta_cols else c,
            inplace=True,
        )
        return df

    def get_df(self):
        self.auto_refresh()
        return self._df

    def auto_refresh(self, force=False):
        if force or (
            datetime.utcnow() - self.timestamp > timedelta(minutes=self.refresh_rate)
        ):
            self._df = self.load_data()
            self.data_cols = self._df.columns.drop(self.meta_cols).to_list()
            self.timestamp = datetime.utcnow()

    def get_country_data(self, country="Germany"):
        df = self.get_df()
        df_country = df[df["Country/Region"] == country]
        return df_country.groupby("Record")[self.data_cols].sum()

    def get_country_total(self, record="Confirmed"):
        df = self.get_df()
        df_record = df[df["Record"] == record]
        df_country = df_record.groupby("Country/Region")[self.data_cols].sum()
        df_total = df_country.iloc[:, -1]
        return df_total.sort_values(ascending=False)

    def get_country_ranking(self):
        country_total = self.get_country_total()
        return country_total.index.to_list()
