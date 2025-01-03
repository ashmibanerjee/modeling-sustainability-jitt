import geopy.distance
import pandas as pd


def calc_distance(lat_1, lng_1, lat_2, lng_2):
    coords_1 = (lat_1, lng_1)
    coords_2 = (lat_2, lng_2)

    return geopy.distance.distance(coords_1, coords_2).km


def get_distances():
    df = pd.read_csv("../../data/connections/city_connections_all.csv")

    df["calc_distance_km"] = df.apply(lambda row: calc_distance(row["lat_1"], row["lng_1"], row["lat_2"], row["lng_2"]), axis=1)

    df.to_csv("../data/city_data/city_connections_calc_dist.csv", index=False)


def get_driving_connections():
    # only filters out the city connections which are within 1000 km
    df = pd.read_csv("../../data/driving_data/city_connections_calc_dist.csv")
    df = df.loc[df["calc_distance_km"] <= 1000]
    df.to_csv("../data/city_data/city_connections_driving.csv", index=False)


if __name__ == '__main__':
    get_driving_connections()