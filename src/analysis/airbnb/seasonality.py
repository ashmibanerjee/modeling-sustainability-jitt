import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from src.analysis.tourmis.preproc import normalize_values


def plot_city_seasonality(city: str, monthly_total_prices: pd.DataFrame):
    # Plotting the seasonality trend
    plt.figure(figsize=(10, 6))
    # plt.plot(monthly_total_prices['month'], monthly_total_prices['difference'], marker='o', label="differnce")
    plt.plot(monthly_total_prices['month'], monthly_total_prices['avg_listing_price_$'], marker='o', label="price_$")
    # plt.plot(monthly_total_prices['month'], monthly_total_prices['avg_listing_adjusted_price_$'], marker='o',
    #          label="adjusted_price_$")

    plt.title(f'Monthly Seasonality Trend for {city}')
    plt.xlabel('Month')
    plt.ylabel('Average Price of all Listings($)')
    plt.legend()
    plt.savefig(f"../../../plots/png/airbnb/seasonality_plots/{city}.png")
    plt.close()


def seasonality_plots():
    airbnb_cities_df = pd.read_csv("../../../data/airbnb_data/airbnb_city_country_mapping.csv", sep=";")
    airbnb_cities = airbnb_cities_df["city"].tolist()

    for city in airbnb_cities:
        print(f"Plotting {city}")
        try:
            file_to_save = f"../../../plots_data/airbnb/seasonality/{city}.csv"
            monthly_total_prices = pd.read_csv(file_to_save)
        except Exception as e:
            print(f"Error reading {city}")
            print(e)
            continue
        plot_city_seasonality(city, monthly_total_prices)


def seasonality_data_preproc():
    airnb_data = pd.read_csv("../../../data/airbnb_data/airbnb_city_country_mapping.csv", sep=";")
    airnbnb_cities = airnb_data["city"].tolist()

    for city in airnbnb_cities:
        try:
            file_to_read = f"../../../plots_data/airbnb/seasonality/{city}.csv"
            monthly_total_prices = pd.read_csv(file_to_read)
            monthly_total_prices["avg_listing_price_normalized"] = normalize_values(monthly_total_prices,
                                                                                    "avg_listing_price_$")
            monthly_total_prices.to_csv(file_to_read, index=False)
        except Exception as e:
            print(f"Error reading {city}")
            print(e)
            continue


if __name__ == "__main__":
    # seasonality_plots()
    seasonality_data_preproc()