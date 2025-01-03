from pathlib import Path
import geopy.distance
import pandas as pd
from itertools import combinations


def get_combinations(vals: list) -> list:
    # Generate all combinations of IATA codes
    combinations_list = list(combinations(vals, 2))

    # Include both (A, B) and (B, A) in the combinations
    combinations_list += [(b, a) for a, b in combinations_list]

    return combinations_list


def get_connections(df: pd.DataFrame, category_col: str) -> pd.DataFrame:
    '''
    This function takes a dataframe and a category and returns a dataframe with all the connections between the values
    :param df:
    :param category: this can be cities or airports etc.
    :return:
    '''

    # Get all the unique values of the category
    vals = df[category_col].unique()

    # Get all the combinations of the unique values
    combinations_list = get_combinations(vals)
    # print(combinations_list)

    # Create a dataframe with all the combinations
    connections_df = pd.DataFrame(combinations_list, columns=[f'{category_col}_1', f'{category_col}_2'])

    connections_df = connections_df.merge(df, left_on=f"{category_col}_1", right_on='city', how='left')
    connections_df = connections_df.rename(columns={'lat': 'lat_1', 'lng': 'lng_1', 'country': 'country_1'})

    connections_df = connections_df.merge(df, left_on=f"{category_col}_2", right_on='city', how='left')
    connections_df = connections_df.rename(columns={'lat': 'lat_2', 'lng': 'lng_2', 'country': 'country_2'})

    connections_df = connections_df[["city_1", "lat_1", "lng_1", "country_1", "city_2", "lat_2", "lng_2", "country_2"]]

    connections_df = connections_df.loc[connections_df["city_1"] != connections_df["city_2"]]
    connections_df = connections_df.reset_index(drop=True)
    return connections_df


def check_if_connection_exists(file_name: str, row: pd.Series) -> pd.DataFrame | None:
    if Path(file_name).exists():
        saved_data = pd.read_csv(file_name)
        saved_data_df = saved_data.loc[(saved_data['city_1'] == row['city_1']) & (
                saved_data['city_2'] == row['city_2'])]
        if saved_data_df.shape[0] > 0:
            print("\t data already saved")
            return saved_data
    return None


def calc_distance(lat_1, lng_1, lat_2, lng_2):
    coords_1 = (lat_1, lng_1)
    coords_2 = (lat_2, lng_2)

    return geopy.distance.geodesic(coords_1, coords_2).km


# Function to categorize distances
def categorize_distance(distance):
    if 0 <= distance < 500:
        return 'very_short_haul'
    elif 500 <= distance < 1500:
        return 'short_haul'
    elif 1500 <= distance < 4000:
        return 'medium_haul'
    else:
        return 'long_haul'


def calc_flight_emissions(category, distance):
    match category:
        case "very_short_haul":
            co2_offset = 155
        case "short_haul":
            co2_offset = 110
        case "medium_haul":
            co2_offset = 75
        case "long_haul":
            co2_offset = 95

    co2_emissions = co2_offset * distance
    return co2_emissions / 1000
