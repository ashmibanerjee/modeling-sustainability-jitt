import pandas as pd
import numpy as np
import sys
import networkx as nx
from trains_estimations import get_train_connections
gamma_ADR = 0.557
gamma_AVC = 0.443

alpha_TT = 0.352
alpha_EM = 0.218
alpha_cost = 0.431

alpha = 0.281
beta = 0.334
gamma = 0.385


def get_normalize_values(l1):
    min_val = min(l1)
    max_val = max(l1)
    norm_vals = [(v - min_val) / (max_val - min_val) for v in l1]
    return norm_vals


def calc_emission_scores(em_merged: pd.DataFrame):
    MODES = ["fly", "driving", "train"]

    ATTRIBUTES = ["_time_hrs", "co2_kg_", '_cost_euro']

    tt_columns = [f"{mode}{attribute}" for mode in MODES for attribute in ATTRIBUTES if "_time_hrs" in attribute]
    co2_columns = [f"{attribute}{mode}" for mode in MODES for attribute in ATTRIBUTES if "co2_kg_" in attribute]
    cost_columns = [f"{mode}{attribute}" for mode in MODES for attribute in ATTRIBUTES if '_cost_euro' in attribute]

    # get_tt normalized
    COLUMNS = [tt_columns, co2_columns, cost_columns]
    WEIGHTS = [alpha_TT, alpha_EM, alpha_cost]
    weighted_vectors = []
    for (column, weight) in zip(COLUMNS, WEIGHTS):
        data = em_merged[column].values[0]
        norm_vals = get_normalize_values(data)
        weighted_norm_vals = [weight * n for n in norm_vals]
        weighted_vectors.append(weighted_norm_vals)
    emission_scores = {}
    for i, mode in enumerate(MODES):
        mode_sum = sum(row[i] for row in weighted_vectors)
        emission_scores[mode] = mode_sum
    min_key = min(emission_scores, key=lambda k: emission_scores[k])
    return min_key, min(emission_scores.values())


def calc_pop_score(destination):
    weighted_popularity_data = pd.read_csv("../../data/user_study/weighted_popularity_city.csv")
    dest_pop = weighted_popularity_data.loc[weighted_popularity_data["city"] == destination]
    if len(dest_pop) == 0:
        return 0
    else:
        return dest_pop["weighted_pop_score"].values[0]


def calc_seasonality_score(dest, month):
    seasonality_data = pd.read_csv("../../plots_data/seasonality/gini/weighted_seasonality.csv")
    dest_seas = seasonality_data.loc[seasonality_data["city"] == dest][month]
    if len(dest_seas) == 0:
        return 0
    else:
        return dest_seas.values[0]


def calc_sf_index(destination: str, month: str, em_merged: pd.DataFrame):
    mode, em_score = calc_emission_scores(em_merged)

    pop_score = calc_pop_score(destination)
    seas_score = calc_seasonality_score(destination, month)
    print(f"\t\tEmission score: {em_score} for Mode: {mode} Popularity Score: {pop_score} Seasonality Score: {seas_score}")
    s_f_index = alpha * em_score + beta * pop_score + gamma * seas_score
    return mode, s_f_index


def merge_emissions_data(starting_city: str, flights: pd.DataFrame, driving_merged: pd.DataFrame,
                         trains_G: nx.classes.digraph.DiGraph):
    em_merged = pd.merge(driving_merged, flights, on=["city_1", "city_2"], how="left")
    em_merged.rename(columns={"co2_kg": "co2_kg_fly"}, inplace=True)

    trains_df = get_train_connections(starting_city, em_merged, trains_G)
    em_merged_all = pd.merge(em_merged, trains_df, on=['city_1', 'city_2'], how="left")
    em_merged_all["train_cost_euro"] = 0.14 * em_merged_all["train_dist_km"]
    return em_merged_all
