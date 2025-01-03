import pandas as pd
from config.constants import GOOGLE_API_KEY
from pathlib import Path
import sys

API_KEY = GOOGLE_API_KEY
ROOT_DIR = Path(__file__).parents[2]
sys.path.append(str(ROOT_DIR))
from utils.api_calls import make_api_call
from utils.connections import check_if_connection_exists

COUNTRIES_SUPPORTED = [
    "Albania",
    "Austria",
    "Belgium",
    "Bosnia and Herzegovina",
    "Bulgaria",
    "Canada",
    "Croatia",
    "Cyprus",
    "Czechia",
    "Denmark",
    "Estonia",
    "Finland",
    "France",
    "Germany",
    "Greece",
    "Hungary",
    "Iceland",
    "Ireland",
    "Italy",
    "Kosovo",
    "Latvia",
    "Liechtenstein",
    "Lithuania",
    "Luxembourg",
    "Malta",
    "Montenegro",
    "Netherlands",
    "North Macedonia",
    "Norway",
    "Poland",
    "Portugal",
    "Romania",
    "Serbia",
    "Slovakia",
    "Slovenia",
    "Spain",
    "Sweden",
    "Switzerland",
    "Turkey",
    "United Kingdom",
    "United States"
]


def get_requests(lat_1, lng_1, lat_2, lng_2):
    # Define the request payload as a Python dictionary
    payload = {
        "origin": {
            "location": {
                "latLng": {
                    "latitude": lat_1,
                    "longitude": lng_1
                }
            }
        },
        "destination": {
            "location": {
                "latLng": {
                    "latitude": lat_2,
                    "longitude": lng_2
                }
            }
        },
        "routeModifiers": {
            "vehicleInfo": {
                "emissionType": "GASOLINE"
            }
        },
        "travelMode": "DRIVE",
        "routingPreference": "TRAFFIC_AWARE_OPTIMAL",
        "extraComputations": ["FUEL_CONSUMPTION"],
        "requestedReferenceRoutes": ["FUEL_EFFICIENT"]
    }

    # Define the headers
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": API_KEY,  # Replace with your actual API key
        "X-Goog-FieldMask": "*"

    }

    # Define the URL
    url = 'https://routes.googleapis.com/directions/v2:computeRoutes'

    # Make the API call
    data = make_api_call(url, "POST", payload, headers)
    return data


def get_connections():
    df = pd.read_csv("../../../data/connections/city_connections_driving.csv")

    print("data frame read, size: ", df.shape)
    df = df.loc[df["country_1"].isin(COUNTRIES_SUPPORTED)]
    print("data frame filtered: ", df.shape)
    file_to_save = "../../../data/driving_data/city_connections_driving_google_raw.csv"
    final_df = None
    column_names = ['city_1', 'city_2', 'distance', 'duration', 'fuel_consumption_microliters', 'comments']
    for idx, row in df.iterrows():
        print(f"\n iteration: {idx} from {row['city_1']} to {row['city_2']}")
        saved_data = check_if_connection_exists(file_to_save, row)
        if saved_data is not None:
            final_df = saved_data
            continue
        response = get_requests(row['lat_1'], row['lng_1'], row['lat_2'], row['lng_2'])
        parsed_response = parse_response(row['city_1'], row['city_2'], response)
        if final_df is None:
            final_df = pd.DataFrame([parsed_response], columns=column_names)
        else:
            final_df = pd.concat([final_df, pd.DataFrame([parsed_response], columns=column_names)], ignore_index=True)
        print("\t connections appended")
        final_df.to_csv(file_to_save, index=False)
        print("\t data saved")


def parse_response(src: str, dest: str, response: dict):
    if response["status_code"] != 200:
        print(f"Request failed with status code: {response['status_code']}")
        return [src, dest, None, None, None, response["message"]]
    distance = response['routes'][0]['legs'][0]["distanceMeters"]
    duration = response['routes'][0]['legs'][0]["duration"]
    fuel_consumption = response['routes'][0]['travelAdvisory']["fuelConsumptionMicroliters"]
    return [src, dest, distance, duration, fuel_consumption, None]


def clean_data():
    df = pd.read_csv("../../../data/driving_data/city_connections_driving_google_raw.csv")
    df = df.dropna(subset=["distance"])
    df['duration_s'] = df["duration"].str.replace("s", "")
    df['duration_s'] = df['duration_s'].astype(int)
    df["distance_km"] = df["distance"] / 1000
    df.drop(columns=["duration", "comments", "distance"], inplace=True)
    df = df[['city_1', 'city_2', 'distance_km', 'duration_s', 'fuel_consumption_microliters']]
    df["CO2_emission_gm"] = df["fuel_consumption_microliters"] /1000000 * 2392
    df.to_csv("../../../data/driving_data/city_connections_driving_google_cleaned.csv", index=False)


if __name__ == "__main__":
    # get_connections()
    clean_data()