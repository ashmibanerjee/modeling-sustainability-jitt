import pandas as pd
import numpy as np
import sys


def get_fuel_prices():
    fuel_price_dict = {"Belgium": 10.10, "Cyprus": 9.88, "Denmark": 10.76, "Finland": 10.75, "France": 9.30,
                       "Germany": 11.74, "Italy": 10.66, "Luxembourg": 9.76, "Netherlands": 12.32, "Norway": 12.86,
                       "Poland": 8.63, "Sweden": 12.54}
    fuel_prices_df = pd.DataFrame(fuel_price_dict.items(), columns=["country", "price_per_km_euro"])
    return fuel_prices_df


def estimate_driving_costs(driving):
    fuel_prices_df = get_fuel_prices()
    for idx, row in driving.iterrows():
        fuel_price = fuel_prices_df.loc[fuel_prices_df["country"] == row["country_1"]]["price_per_km_euro"]

        if len(fuel_price) == 0:
            fuel_price = fuel_prices_df.loc[fuel_prices_df["country"] == row["country_2"]]["price_per_km_euro"]
        driving["cost_offset"] = fuel_price.values[0]
        driving["driving_cost_euro"] = driving["driving_dist_km"] * driving["cost_offset"] / 100
        driving.drop(columns=["cost_offset"], inplace=True)
        return driving


def merge_driving_data(starting_city: str, driving_google: pd.DataFrame, driving_osrm: pd.DataFrame):
    """
    Function to merge the driving data from google and osrm such that only the most sustainable option is considered
    i.e. min distance
    """
    driving_google = driving_google.loc[driving_google["city_1"] == starting_city]
    driving_em_osrm = driving_osrm.loc[driving_osrm["city_1"] == starting_city]
    if len(driving_google) == 0 and len(driving_em_osrm) == 0:
        print(f"Data not found for {starting_city}")
        return None
    driving_google = driving_google.sort_values(by=["co2_kg_dist_google"])
    driving_google.drop_duplicates(subset=["city_1", "city_2"], inplace=True)
    driving_google.drop(columns=["duration_sec_google"], inplace=True)

    driving_em_osrm = driving_em_osrm.sort_values(by=["co2_kg_dist_osrm"])
    driving_em_osrm.drop_duplicates(subset=["city_2"], inplace=True)
    driving_em_osrm = driving_em_osrm[
        ["city_1", "city_2", "country_1", "country_2", "dist_km", "duration_hrs", "co2_kg_dist_osrm"]]
    driving_em_osrm.rename(columns={"dist_km": "dist_km_osrm", "duration_hrs": "duration_hrs_osrm"}, inplace=True)

    driving_merged = pd.merge(driving_em_osrm, driving_google, on=["city_1", "city_2"], how="left")
    driving_merged['co2_kg_driving'] = driving_merged.apply(
        lambda row: min(row['co2_kg_dist_osrm'], row['co2_kg_dist_google']), axis=1)
    driving_merged['driving_dist_km'] = driving_merged.apply(
        lambda row: min(row['dist_km_osrm'], row['dist_km_google']), axis=1)
    driving_merged['driving_time_hrs'] = driving_merged.apply(
        lambda row: min(row['duration_hrs_osrm'], row['duration_hrs_google']), axis=1)

    driving_merged = driving_merged[
        ["city_1", "city_2", "country_1", "country_2", "driving_dist_km", "driving_time_hrs", "co2_kg_driving"]]
    driving_merged.drop_duplicates(subset=["city_2"], inplace=True)
    driving_merged = estimate_driving_costs(driving_merged)
    return driving_merged
