import pandas as pd
from datetime import datetime, timedelta


class CSSEData(object):
    url_pattern = (
        "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/"
        "csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-{}.csv"
    )

    def __init__(self, refresh_rate=30):
        self.refresh_rate = timedelta(minutes=refresh_rate)
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
        return df

    def preprocess(self, df):
        df.drop(columns=["Province/State", "Lat", "Long"], inplace=True)
        df.rename(
            columns=lambda c: pd.to_datetime(c)
            if c not in ["Country/Region", "Record"]
            else c,
            inplace=True,
        )
        df_country = df.groupby(["Country/Region", "Record"]).sum()
        df_country.reset_index(level=1, drop=False, inplace=True)

        # calculate active cases
        data_cols = df_country.columns.drop("Record")
        df_confirmed = df_country[df_country["Record"] == "Confirmed"][data_cols]
        df_recovered = df_country[df_country["Record"] == "Recovered"][data_cols]
        df_dead = df_country[df_country["Record"] == "Deaths"][data_cols]
        df_active = df_confirmed - df_recovered - df_dead
        df_active["Record"] = "Active"
        return pd.concat([df_country, df_active])

    def auto_refresh(self, force=False):
        if force or (datetime.utcnow() - self._ts > self.refresh_rate):
            df = self.load_data()
            self._df = self.preprocess(df)
            self._ts = datetime.utcnow()
            self.data_cols = self._df.columns.drop("Record").to_list()

    def get_df(self):
        self.auto_refresh()
        return self._df

    def get_country_data(self, country="Germany"):
        df = self.get_df()
        df_country = df.loc[country].reset_index(drop=True).set_index("Record")
        return df_country.loc[:, (df_country != 0).any(axis=0)]

    def get_country_total(self, record="Active"):
        df = self.get_df()
        df_record = df[df["Record"] == record]
        return df_record.iloc[:, -1].sort_values(ascending=False)

    def get_country_ranking(self):
        country_total = self.get_country_total(record="Active")
        return country_total.index.to_list()
