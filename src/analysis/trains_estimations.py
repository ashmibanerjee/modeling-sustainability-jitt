import pandas as pd
import numpy as np
import sys
import networkx as nx

sys.path.append('../../')
from src.data_gathering.trains.db_routes import find_connections


def get_train_connections(STARTING_POINT, em_merged, trains_G):
    destinations = em_merged["city_2"].tolist()
    emissions = []
    durations = []
    distances = []
    for dest in destinations:
        co2, tt, dist = find_connections(trains_G, STARTING_POINT, dest)
        emissions.append(co2)
        durations.append(tt)
        distances.append(dist)
    train_data = {"city_2": destinations, 'co2_kg_train': emissions, 'train_time_hrs': durations,
                  'train_dist_km': distances}
    train_df = pd.DataFrame(train_data)
    train_df["city_1"] = STARTING_POINT
    return train_df
