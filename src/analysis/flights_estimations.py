import pandas as pd


def estimate_trip_costs_fly(flights):
    costs_df = pd.read_csv("../../data/flights_data/airline_costs_merged.csv")
    costs_df = costs_df[["Airline", "intl_cost_per_km_euros", "domestic_cost_per_km_euros"]]
    flights['Airline'] = flights['Airline'].str.split(',').str[0].str.strip()  # considering only the first airline

    merged_df = pd.merge(flights, costs_df, on='Airline', how='left')

    merged_df['cost_offset'] = merged_df["intl_cost_per_km_euros"]
    domestic_condition = (merged_df['src_country'] == merged_df['dest_country']) & (
        ~merged_df['domestic_cost_per_km_euros'].isna())

    merged_df['cost_offset'] = merged_df['domestic_cost_per_km_euros'].where(domestic_condition,
                                                                             merged_df['intl_cost_per_km_euros'])

    merged_df['fly_cost_euro'] = merged_df["cost_offset"] * merged_df["gcd_updated_km"]
    return merged_df


def categorize_distance(distance):
    max_distance = 5000
    step = 100
    num_categories = max_distance // step

    for category in range(1, num_categories + 1):
        if (category - 1) * step <= distance < category * step:
            return category

    return num_categories + 1  # Default category if distance exceeds the defined ranges


def estimate_flying_time(flights):
    """
    Function to estimate the flying time for nans based on the average flying time for the category
    :param flights:
    :return: pd.DataFrame
    """
    flights["fly_time_hrs"] = flights["Duration_hrs"] + flights["Duration_mins"] / 60
    flights["category"] = flights.apply(
        lambda row: categorize_distance(row['gcd_updated_km'])
        , axis=1)
    category_groups = pd.DataFrame(flights.groupby("category")["fly_time_hrs"].mean())
    category_groups = category_groups.reset_index()
    category_groups = category_groups.rename(columns={"fly_time_hrs": "avg_time_hrs"})

    merged_df = pd.merge(flights, category_groups, on='category', how='left')
    merged_df['fly_time_hrs'].fillna(merged_df['avg_time_hrs'], inplace=True)

    # Drop the unnecessary columns
    result_df = merged_df.drop(columns=['avg_time_hrs'])
    return result_df


def adjust_flights_data(flights, STARTING_CITY):
    # We compute the flying time for all flights before filtering out the flights from the starting city to avoid
    # nans in flying time
    flights = estimate_flying_time(flights)
    flights = flights.loc[flights["city_1"] == STARTING_CITY]
    flights = flights.sort_values(by=["co2_kg"])
    flights.drop_duplicates(subset=["destination"], inplace=True)
    flights.loc[flights['Airline'].str.contains('Separate Tickets', case=False, na=False), 'Airline'] = 'No data'

    flights = estimate_trip_costs_fly(flights)

    flights = flights[
        ["source", "city_1", "destination", "city_2", "Airline", "fly_time_hrs", "gcd_updated_km", "co2_kg",
         "fly_cost_euro"]]
    flights.rename(columns={"Duration_hrs": "fly_time_hrs", "gcd_updated_km": "fly_dist_km"}, inplace=True)

    return flights.reset_index(drop=True)
