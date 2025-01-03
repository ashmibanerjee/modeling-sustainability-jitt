import pandas as pd
import sys
import networkx as nx


def convert_graph():
    graph_file_name = "../../../../data/emissions/db_routes_with_co2.graphml"
    G = nx.read_graphml(graph_file_name)

    edges_with_attributes = []
    for u, v, data in G.edges(data=True):
        edge_data = {
            "Source": u,
            "Target": v,
            "train_number": data.get("train_number", None),
            "time_taken": data.get("time_taken", None),
            "distance_km": data.get("distance_km", None),
            "co2_kg": data.get("co2_kg", None),
        }
        edges_with_attributes.append(edge_data)

    df = pd.DataFrame(edges_with_attributes)
    excel_file_name = "../../../../data/emissions/db_routes_with_co2.xlsx"
    df.to_excel(excel_file_name, index=False)

    print(f"Graph data has been saved to {excel_file_name}")


convert_graph()
