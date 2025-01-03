from pathlib import Path

import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import pickle


def create_graph(df: pd.DataFrame, src_col_name: str, dest_col_name: str, train_number: str, edge_count: int):
    # Create a directed graph
    G = nx.DiGraph()
    edges = 0
    # Add edges to the graph
    for i, row in df.iterrows():
        src = row[src_col_name]
        dest = row[dest_col_name]
        try:
            time_taken = pd.to_datetime(df.loc[i + 1, 'exp_arr']) - pd.to_datetime(df.loc[i, 'exp_arr'])
            time_taken = int(time_taken.total_seconds())
        except (KeyError, ValueError):
            time_taken = 0
        if edges < edge_count:
            G.add_edge(src, dest, train_number=train_number, time_taken=time_taken)
            edges += 1
        else:
            break
    return G


def match_station_name(station_name: str) -> str:
    match station_name:
        case "Munich":
            station_name = "München Hbf"
        case "Cologne":
            station_name = "Köln Hbf"
        case "Frankfurt":
            station_name = "Frankfurt (Main) Hbf"
        case "Nurembourg":
            station_name = "Nürnberg Hbf"
        case "Vienna":
            station_name = "Wien Hbf"
        case "Zurich":
            station_name = "Zürich HB"
        case "Neumunster":
            station_name = "Neumünster"
        case "Neumuenster":
            station_name = "Neumünster"
        case "Duesseldorf":
            station_name = "Düsseldorf Hbf"
        case "Saarbrucken":
            station_name = "Saarbrücken Hbf"
        case "Hamburg":
            station_name = "Hamburg Hbf"
    return station_name


# Function to find connections between two stations
def find_connections(graph, station1, station2, display_network=False):
    station1 = match_station_name(station1)
    station2 = match_station_name(station2)
    if "hbf" not in station1.lower():
        station1 += " Hbf"
    if "hbf" not in station2.lower():
        station2 += " Hbf"

    try:
        # Find the shortest path between two stations
        path = nx.shortest_path(graph, source=station1, target=station2)
        # Calculate total time for the entire journey
        total_time = sum(graph[path[i]][path[i + 1]]['time_taken'] for i in range(len(path) - 1))

        total_distance = sum(graph[path[i]][path[i + 1]]['distance_km'] for i in range(len(path) - 1))

        total_co2_kg = sum(graph[path[i]][path[i + 1]]['co2_kg'] for i in range(len(path) - 1))
        # Print the path
        if display_network:
            print(f"Total CO2 emissions: {total_co2_kg} kg")
            print(f"Total time taken: {total_time / 3600} hours")
            print(f"Total distance: {total_distance} km")
            print(f"Connections from {station1} to {station2}:")
            for i in range(len(path) - 1):
                current_station = path[i]
                next_station = path[i + 1]
                train_number = graph[current_station][next_station]['train_number']
                time_taken = graph[current_station][next_station]['time_taken']
                print(f"   {current_station} to {next_station} (Train ICE{train_number}) time taken {time_taken}")
        return [total_co2_kg, total_time / 3600, total_distance]
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        if display_network:
            print(f"No direct connection found between {station1} and {station2} in our database")
        return [None, None, None]

def compute_routes(file_to_save: str):
    df = pd.read_csv("../../../data/trains_data/emil_db_cleaned.csv", low_memory=False)
    df = df.drop_duplicates()
    routes = df.groupby(['start_date', 'train_number', 'trip_id'])
    G = []
    for name, route_df in routes:
        stops_until_dest = route_df.loc[route_df["stop_number"] == 0]["stops_until_dest"].values[0]
        train_number = name[1]
        g_route = create_graph(route_df, "station", "next_station", train_number, edge_count=stops_until_dest)
        G.append(g_route)
    C = nx.compose_all(G)
    # save graph object to file
    nx.write_graphml(C, file_to_save)
    print("Graph computed with ", C.number_of_nodes(), " nodes and ", C.number_of_edges(), " edges")
    return C


def load_connections(file_name: str):
    try:
        print("Loading graph from file")
        loaded_G = nx.read_graphml(file_name)
        return loaded_G
    except FileNotFoundError:
        print("File not found, computing graph")
        return compute_routes(file_name)


if __name__ == '__main__':
    file_path = "../../../data/trains_data/db_routes.graphml"
    # compute_routes(file_path)
    G = load_connections(file_path)
    find_connections(G, 'Berlin Hbf (tief)', 'Wien Hbf')
