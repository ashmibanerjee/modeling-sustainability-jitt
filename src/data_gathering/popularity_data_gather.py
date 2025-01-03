from pathlib import Path

from data_scraper import scraper
import pandas as pd


def compute_city_popularities():
    df = pd.read_csv("../../plots_data/eu_cities_with_airports.csv")

    cities = df["city_ascii"].unique().tolist()
    print(f"City count: {len(cities)}")

    column_names = ["city", "review_count", "number_of_attractions", "attraction_reviews", "attraction_photos",
                    "local_time"]

    file_name = '../../data/tripadvisor_data/cities_popularity_raw.csv'
    final_df = None
    for idx, city in enumerate(cities):
        print(f"\niteration {idx}: {city}")
        # skipping the cities which have already been scraped
        if Path(file_name).exists():
            saved_data = pd.read_csv(file_name)
            if city in saved_data["city"].unique():
                print(f"\t {city} already saved")
                final_df = saved_data
                continue
        data = scraper(city, category="reviews")
        if final_df is None:
            final_df = pd.DataFrame([data], columns=column_names)
        else:
            final_df = pd.concat([final_df, pd.DataFrame([data], columns=column_names)], ignore_index=True)
        print("\t population data appended")
        final_df.to_csv(file_name, index=False, encoding='utf-8')
        print("\t population data saved")


def clean_popularity_data():
    df = pd.read_csv("../../data/tripadvisor_data/cities_popularity_raw.csv")
    df.fillna(0, inplace=True)
    df["review_count"] = df["review_count"].str.replace(',', '')
    df["number_of_attractions"] = df["number_of_attractions"].str.replace(',', '')
    df["attraction_reviews"] = df["attraction_reviews"].str.replace(',', '')
    df["attraction_photos"] = df["attraction_photos"].str.replace(',', '')

    df["review_count"] = df["review_count"].str.replace(" reviews and opinions", "")

    df["review_count"] = df["review_count"].astype(int)
    df["number_of_attractions"] = df["number_of_attractions"].fillna("0")
    df["number_of_attractions"] = df["number_of_attractions"].astype(int)

    df["attraction_reviews"] = df["attraction_reviews"].fillna("0")
    df["attraction_reviews"] = df["attraction_reviews"].astype(int)

    df["attraction_photos"] = df["attraction_photos"].fillna("0")
    df["attraction_photos"] = df["attraction_photos"].astype(int)

    df.to_csv("../data/final_data/clean/cities_popularity_cleaned.csv", index=False, encoding='utf-8')


if __name__ == '__main__':
    # compute_city_popularities()
    clean_popularity_data()