from pathlib import Path
import numpy as np
import pandas as pd
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).parents[2]
sys.path.append(str(ROOT_DIR))
from utils.api_calls import make_api_call


def get_request(lat_1, lng_1, lat_2, lng_2):
    url = f"http://router.project-osrm.org/route/v1/driving/{lng_1},{lat_1};{lng_2}," \
          f"{lat_2}?overview=false&steps=false&annotations=false"

    data = make_api_call(url, "GET")
    return data


def parse_driving_info(lat_1, lng_1, lat_2, lng_2):
    data = get_request(lat_1, lng_1, lat_2, lng_2)
    if data["code"] == "Ok":

        distance = data["routes"][0]["distance"] / 1000
        duration = data["routes"][0]["duration"]
        print(f"\t distance: {distance} km, duration: {duration} sec")
        return [distance, duration]
    else:
        return [np.nan, np.nan]


def compute_driving_info_cities():
    df = pd.read_csv("../../../data/connections/city_connections_driving.csv")
    print(f"data frame read, size: {df.shape}")

    column_names = df.columns.tolist()
    column_names.extend(["dist_km", "duration_sec"])
    final_df = None
    file_name = "../../../data/driving_data/city_connections_driving_osrm.csv"
    for idx, row in df.iterrows():
        print(f"\n iteration: {idx}, city: {row['city_1']} to {row['city_2']}")
        if Path(file_name).exists():
            saved_data = pd.read_csv(file_name)
            saved_data_df = saved_data.loc[(saved_data['city_1'] == row['city_1']) & (
                    saved_data['city_2'] == row['city_2'])]
            if saved_data_df.shape[0] > 0:
                print("\t data already saved")
                final_df = saved_data
                continue
        driving_info = parse_driving_info(row['lat_1'], row['lng_1'], row['lat_2'], row['lng_2'])
        data = row.values.tolist()
        data.extend(driving_info)
        if final_df is None:
            final_df = pd.DataFrame([data], columns=column_names)
        else:
            final_df = pd.concat([final_df, pd.DataFrame([data], columns=column_names)], ignore_index=True)
        print("\t data appended")
        final_df.to_csv(file_name, index=False)
        print("\t data saved")


if __name__ == '__main__':
    compute_driving_info_cities()
