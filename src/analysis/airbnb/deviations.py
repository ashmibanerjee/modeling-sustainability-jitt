from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import os, glob
import numpy as np


def preproc_airbnb_data(df: pd.DataFrame) -> pd.DataFrame:
    df["price"] = df["price"].str.replace("$", "")
    df["price"] = df["price"].str.replace(",", "")
    df["price"] = df["price"].astype(float)
    df.rename(columns={"price": "price_$"}, inplace=True)

    df["adjusted_price"] = df["adjusted_price"].str.replace("$", "")
    df["adjusted_price"] = df["adjusted_price"].str.replace(",", "")
    df["adjusted_price"] = df["adjusted_price"].astype(float)
    df.rename(columns={"adjusted_price": "adjusted_price_$"}, inplace=True)
    df.available.replace(('t', 'f'), (1, 0), inplace=True)
    df['date'] = pd.to_datetime(df['date'])
    df = df.loc[df["available"] == 1]
    return df


def calc_daily_deviations(df: pd.DataFrame) -> pd.DataFrame:
    df_groupby = df.groupby(["date"])
    total_deviation_per_day = df_groupby.agg({
        'price_$': 'sum',
        'adjusted_price_$': 'sum',
        'listing_id': 'count'
    })
    total_deviation_per_day.rename(columns={"listing_id": "listing_count", "price_$": "total_price_$",
                                            "adjusted_price_$": "total_adjusted_price_$"}, inplace=True)
    total_deviation_per_day["avg_price_$"] = total_deviation_per_day["total_price_$"] / total_deviation_per_day[
        "listing_count"]
    total_deviation_per_day["avg_adjusted_price_$"] = total_deviation_per_day["total_adjusted_price_$"] / \
                                                      total_deviation_per_day["listing_count"]
    total_deviation_per_day["difference"] = total_deviation_per_day['avg_price_$'] - total_deviation_per_day[
        "avg_adjusted_price_$"]
    total_deviation_per_day.reset_index(inplace=True)
    total_deviation_per_day["date"] = pd.to_datetime(total_deviation_per_day['date'])
    total_deviation_per_day["month"] = total_deviation_per_day['date'].dt.month
    total_deviation_per_day['year'] = total_deviation_per_day["date"].dt.year
    total_deviation_per_day["day"] = total_deviation_per_day["date"].dt.day

    return total_deviation_per_day


def calc_monthly_deviations(total_deviation_per_day: pd.DataFrame):
    monthly_total_prices = total_deviation_per_day.groupby(['month'])[
        ["avg_price_$", "avg_adjusted_price_$"]].sum().reset_index()
    monthly_total_prices["difference"] = monthly_total_prices["avg_price_$"] - monthly_total_prices[
        "avg_adjusted_price_$"]
    monthly_total_prices.rename(
        columns={"avg_price_$": "total_price_$", "avg_adjusted_price_$": "total_adjusted_price_$"}, inplace=True)
    monthly_total_prices["avg_listing_price_$"] = monthly_total_prices["total_price_$"] / 30
    monthly_total_prices["avg_listing_adjusted_price_$"] = monthly_total_prices["total_adjusted_price_$"] / 30
    monthly_total_prices["avg_diff"] = monthly_total_prices["avg_listing_price_$"] - monthly_total_prices[
        "avg_listing_adjusted_price_$"]
    return monthly_total_prices


def calc_deviations_for_cities():
    airbnb_cities_df = pd.read_csv("../../../data/airbnb_data/airbnb_city_country_mapping.csv", sep=";")
    airbnb_cities = airbnb_cities_df["city"].tolist()

    for city in airbnb_cities:
        print(f"Processing {city}")
        try:
            all_files = glob.glob(os.path.join("../../../data/airbnb_data/calendar_data/", city.lower() + "*.csv.gz"))
            df = pd.read_csv(all_files[0], compression="gzip")
        except Exception as e:
            print(f"Error reading {city}")
            print(e)
            continue
        df = preproc_airbnb_data(df)
        file_to_save = f"../../../plots_data/airbnb/seasonality/{city}.csv"
        if Path(file_to_save).is_file():
            print(f"File {file_to_save} already exists")
            continue
        total_deviation_per_day = calc_daily_deviations(df)
        monthly_total_prices = calc_monthly_deviations(total_deviation_per_day)
        monthly_total_prices.to_csv(file_to_save, index=False)
        # plot_city_seasonality(city, monthly_total_prices)


def calculate_avg_daily_rate(df: pd.DataFrame) -> pd.DataFrame:
    daily_dev_df = calc_daily_deviations(df)
    daily_dev_df = daily_dev_df[["date", "listing_count", "avg_price_$", "day", "month", "year"]]
    daily_dev_df.rename(columns={"avg_price_$": "adr_$"}, inplace=True)
    return daily_dev_df


if __name__ == "__main__":
    calc_deviations_for_cities()
