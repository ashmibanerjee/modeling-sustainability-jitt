import pandas as pd


def skip_iterations(file_name: str):
    pass


def normalize_values(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    col_values = df[column_name]
    # Calculate the min and max values
    min_value = col_values.min()
    max_value = col_values.max()

    normalized_vals = (col_values - min_value) / (max_value - min_value)

    return normalized_vals


def replace_header_row(df: pd.DataFrame) -> pd.DataFrame:
    new_header = df.iloc[0]  # grab the first row for the header
    df = df[1:]  # take the data less the header row
    df.columns = new_header  # set the header row as the df header
    return df
