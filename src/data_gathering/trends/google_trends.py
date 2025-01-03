# Setup and Import Required Libraries
import time
from pathlib import Path

import pandas as pd
from pytrends.request import TrendReq
from random import randrange

MAX_TRIES = 5


def get_trends(kw_list):
    print(kw_list)
    tries = 0
    while tries < MAX_TRIES:
        try:
            pytrends = TrendReq(hl='en-US', tz=360, timeout=(10, 25))

            # build payload

            # cat=67 is for travel
            pytrends.build_payload(kw_list, cat=67, timeframe='today 5-y', gprop="images")

            # 1 Interest over Time
            data = pytrends.interest_over_time()
            data = data.reset_index()
            return data
        except Exception as e:
            tries += 1
            print(f"Error while scraping for {kw_list} for try nr: {tries}: {e}")
            sleep_time = randrange(10) * 10
            print("pausing for " + str(sleep_time) + " seconds")
            time.sleep(sleep_time)


def get_city_trends(city_data_file: str = "../../../data/city_data/eu_cities_with_airports.csv", save_data_file: str = "../../../data/trends_data/city_trends_images_raw_v2.csv"):
    df = pd.read_csv(city_data_file)
    if "city_ascii" in df.columns:
        city_list = df['city_ascii'].tolist()

    else:
        city_list = df['city'].tolist()
    countries = df['country'].tolist()
    kw_list = [f"{city}, {country}" for city, country in zip(city_list, countries)]
    kw_list = list(set(kw_list))
    kw_list = sorted(kw_list)
    batch_size = 5
    batches = [kw_list[i:i + batch_size] for i in range(0, len(kw_list), batch_size)]

    final_df = None

    for batch in batches:
        if Path(save_data_file).exists():
            saved_data = pd.read_csv(save_data_file)
            if set(batch).issubset(list(saved_data)):
                print(f"\t {batch} already saved")
                final_df = saved_data
                continue
        batch_trends = get_trends(batch)
        # if batch_trends["date"].dtype != "0":
        batch_trends["date"] = batch_trends["date"].astype(str)
        if "isPartial" in batch_trends.columns:
            batch_trends = batch_trends.drop(columns=["isPartial"])
        if final_df is None:
            final_df = batch_trends
        else:
            final_df = final_df.merge(batch_trends, on="date", how="right")
        final_df.to_csv(save_data_file, index=False, encoding='utf-8')
        print("\t data saved")
        time.sleep(10)


if __name__ == '__main__':
    # get_city_trends(city_data_file="../../../data/trends_data/zero_val_cities_debug.csv", save_data_file="../../../data/trends_data/city_trends_zero_debug.csv")
    get_city_trends()