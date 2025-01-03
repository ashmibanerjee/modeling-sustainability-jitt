import pandas as pd
import sys
import networkx as nx
sys.path.append("../..")
from utils.connections import categorize_distance, calc_flight_emissions


def driving_emissions_calc():
    df = pd.read_csv("../../data/driving_data/city_connections_driving_osrm.csv")
    df["estd_emissions_gm"] = df["calc_distance_km"] * 127
    df["estd_emissions_osrm_gm"] = df["dist_km"] * 127
    df.to_csv("../../data/emissions/city_connections_driving_emissions.csv", index=False)


def train_emissions_calc():
    graph_file_name = "../../data/trains_data/db_routes_with_distances.graphml"
    G =nx.read_graphml(graph_file_name)
    routes = list(G.edges)

    for route in routes:
        distance = G[route[0]][route[1]]['distance_km']
        G[route[0]][route[1]]['co2_kg'] = distance * 24/1000
    file_to_save = "../../data/emissions/db_routes_with_co2.graphml"
    nx.write_graphml(G, file_to_save)


def flight_emissions_calc(df: pd.DataFrame):
    df["category"] = df.apply(
        lambda row: categorize_distance(row['distance_km'])
        , axis=1)
    df["co2_kg"] = df.apply(lambda row: calc_flight_emissions(row['category'], row['distance_km']), axis=1)


def calc_emissions(mode: str = "driving", df: pd.DataFrame = None):
    match mode:
        case "driving":
            driving_emissions_calc()
        case "train":
            train_emissions_calc()
        case "flight":
            flight_emissions_calc(df)


if __name__ == '__main__':
    calc_emissions(mode="train")
