import pandas as pd


def normalize_values(df, column_name):
    col_values = df[column_name]
    # Calculate the min and max values
    min_value = col_values.min()
    max_value = col_values.max()

    normalized_vals = (col_values - min_value) / (max_value - min_value)

    return normalized_vals


def preproc_tourmis_data(inhalt_label="APREF"):
    data = pd.read_csv("../../../data/tourmis_data/tourmis_seasonality_cleaned.csv")
    data = data.loc[data["inhalt_label"] == inhalt_label]
    tourmis_cities = data["city"].unique().tolist()
    data.drop(columns=["inhalt_label", "total_2022"], inplace=True)
    data.reset_index(inplace=True, drop=True)

    df_T = data.T
    df_T.reset_index(inplace=True)
    new_header = df_T.iloc[0]  # grab the first row for the header
    df_T = df_T[1:]  # take the data less the header row
    df_T.columns = new_header  # set the header row as the df header
    df_T.rename(columns={"city": "month"}, inplace=True)

    for city in tourmis_cities:
        df_T[city] = df_T[city].astype(float)
        df_T[city] = normalize_values(df_T, city)
    df_T.to_csv(f"../../../plots_data/tourmis/tourmis_cities_normalized_{inhalt_label}.csv", index=False)


if __name__ == "__main__":
    INHALT_LABELS = ["APREF", "NPREF"]
    for inhalt_label in INHALT_LABELS:
        preproc_tourmis_data(inhalt_label=inhalt_label)