import pandas as pd
import requests
from datetime import datetime
import glob, os
import calendar

def generate_days(year, month):
    days_in_month = calendar.monthrange(year, month)[1]
    days_list = [f"{year}-{month:02d}-{day:02d}" for day in range(1, days_in_month + 1)]
    return days_list


def form_url(city: str, country: str, neighbourhood: str):
    date_options = generate_days(2023, 9)
    country = country.lower().replace(" ", "-")

    # TODO: change this for some countries - Spain, and others
    neighbourhood = neighbourhood.lower().replace(" ", "-")

    for date_option in date_options:
        url = f"http://data.insideairbnb.com/{country}/{neighbourhood}/{city.lower()}/{date_option}/data/calendar.csv.gz"
        file_name = city.lower().replace(" ", "_") + "-" + date_option + ".csv.gz"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                download_data(response.content, file_name)
                break
        except Exception as e:
            print(f"Error downloading {file_name}")
            print(e)
            continue


def download_data(content, file_name):
    file_path = "../../../data/airbnb_data/calendar_data/"
    print(f"Downloading {file_name}")
    with open(file_path+file_name, "wb") as f:
        f.write(content)
        f.close()
    print(f"Downloaded {file_name}")


def gather_all_cities_data():
    city_country_df = pd.read_csv("../../../data/airbnb_data/airbnb_city_country_mapping.csv", sep=";")
    for index, row in city_country_df.iterrows():
        city = row["city"]
        country = row["country"]
        neighbourhood = row["Neighbourhood"]
        form_url(city=city, country=country, neighbourhood=neighbourhood)


def merge_files():
    file_path = "../../../data/airbnb_data/calendar_data/"
    city_name = "amsterdam"
    all_files = glob.glob(os.path.join(file_path, city_name + "*.csv.gz"))
    final_df = None
    for file in all_files:
        print(f"Reading {file}")
        df = pd.read_csv(file, compression="gzip")
        if final_df is None:
            final_df = df
        else:
            final_df = pd.concat([final_df, df])
    final_df.to_csv("../../../data/airbnb_data/airbnb_cities_data.csv", index=False)


if __name__ == '__main__':
    gather_all_cities_data()
# "http://data.insideairbnb.com/the-netherlands/north-holland/amsterdam/2023-09-03/data/calendar.csv.gz"
