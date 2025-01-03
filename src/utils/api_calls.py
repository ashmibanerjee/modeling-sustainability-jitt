import json
import pandas as pd
import requests
from typing import Optional


def make_api_call(url: str, request_type: str, payload: Optional[dict] = None, headers: Optional[dict] = None) -> dict | None:
    match request_type:
        case "GET":
            response = requests.get(url)
        case "POST":
            response = requests.post(url, data=json.dumps(payload), headers=headers)
        case _:
            print(f"Invalid request type: {request_type}")
            return None
    try:
        data = response.json()
        if "error" in data.keys():
            data["status_code"] = data["error"]["code"]
            data["message"] = data["error"]["message"]
        if "status_code" not in data.keys():
            data["status_code"] = 200
        print("\t request successful")
    except Exception as e:
        print(e)
        print(f"\t Request failed with status code: {response.status_code}")
        data = {"message": e, "code": "InvalidQuery", "status_code": response.status_code}
    return data


def postprocess_data(api_data, row_vals, final_df, column_names):
    row_vals.extend(api_data)
    if final_df is None:
        final_df = pd.DataFrame([row_vals], columns=column_names)
    else:
        final_df = pd.concat([final_df, pd.DataFrame([row_vals], columns=column_names)], ignore_index=True)
    return final_df
