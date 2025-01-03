import pandas as pd


def get_common_cities(airbnb_cities_df, tourmis_cities_df):
    airbnb_cities = airbnb_cities_df["city"].tolist()
    tourmis_cities = list(tourmis_cities_df.columns)[1:]

    common_cities = list(set(airbnb_cities).intersection(tourmis_cities))
    return common_cities


def preproc_seasonality_airbnb_tourmis(inhalt_label="APREF"):
    airbnb_cities_df = pd.read_csv("../../data/airbnb_data/airbnb_city_country_mapping.csv", sep=";")

    tourmis_cities_df = pd.read_csv(f"../../plots_data/tourmis/tourmis_cities_normalized_{inhalt_label}.csv")

    common_cities = get_common_cities(airbnb_cities_df, tourmis_cities_df)
    for common_city in common_cities:
        try:
            airbnb_data = pd.read_csv(f"../../plots_data/airbnb/seasonality/{common_city}.csv")
            city_data = airbnb_data[["month", "avg_listing_price_normalized"]]
            column_name = f"normalized_{inhalt_label}_2022"
            city_data[column_name] = tourmis_cities_df[common_city]
            city_data.to_csv(f"../../plots_data/seasonality/airbnb_x_tourmis/{common_city}_{inhalt_label}.csv", index=False)
            print(f"common city done for {common_city}")
        except Exception as e:
            print(f"Error reading {common_city}")
            print(e)
            continue


if __name__ == "__main__":
    INHALT_LABELS = ["APREF", "NPREF"]
    for inhalt_label in INHALT_LABELS:
        preproc_seasonality_airbnb_tourmis(inhalt_label=inhalt_label)