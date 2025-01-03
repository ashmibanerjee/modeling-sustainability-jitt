import pandas as pd
import numpy as np


def calculate_gini_coefficients_monthly_data(df: pd.DataFrame) -> pd.DataFrame:
    '''
    This function calculates the gini coefficients for the monthly data and assigns a yearly score to each city
    :param df:
    :return:
    '''
    if "inhalt_label" in df.columns:
        df = df.drop(columns=["inhalt_label"])
    try:
        grouped_df = df.groupby(['city']).sum().drop(['total_2022'], axis=1)
    except:
        grouped_df = df.groupby(['city']).sum()
    n = len(grouped_df.columns)
    xi = grouped_df.values
    gini_coefficient = calc_gini(n, xi)

    # Create a new DataFrame with city names and corresponding Gini coefficients
    result_df = pd.DataFrame({'city': grouped_df.index, 'gini_coeff': gini_coefficient})
    result_df = result_df.sort_values(by="gini_coeff", ascending=False).reset_index(drop=True)
    print(result_df["city"].tolist())
    return result_df


def calc_gini(n, xi):
    xi_sorted = np.sort(xi, axis=1)
    rank_i = np.arange(1, n + 1)
    gini_coefficient = (2 * np.sum(rank_i * xi_sorted, axis=1) - (n + 1) * np.sum(xi_sorted, axis=1)) / (
            n * np.sum(xi_sorted, axis=1))
    return gini_coefficient


def calculate_gini_coefficients_daily_data(df: pd.DataFrame, city_name: str = "Amsterdam", column_name:str = "adr_$") -> pd.DataFrame:
    grouped_df = df.groupby("month")
    gini_indices_monthly = {key: 0 for key in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]}
    for name, group in grouped_df:
        #     print(group)
        gini_indices_monthly[name] = gini(group[column_name])
    gini_df = pd.DataFrame(gini_indices_monthly.items(), columns=["month", "gini_coeff_adr"])
    gini_df_T = gini_df.T
    gini_df_T.reset_index(drop=True, inplace=True)
    gini_df_T = gini_df_T[1:]
    gini_df_T["city"] = city_name
    gini_df_T.columns = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep",
                         "Oct", "Nov", "Dec", "city"]
    gini_df_T = gini_df_T[["city", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep",
                           "Oct", "Nov", "Dec"]]
    return gini_df_T


def gini(list_of_values):
    sorted_list = sorted(list_of_values)
    height, area = 0, 0
    fair_area = 1  # initialize with any value except 0
    for value in sorted_list:
        height += value
        area += height - value / 2.
        fair_area = height * len(list_of_values) / 2
    return (fair_area - area) / fair_area


def calculate_gini_coefficients(df: pd.DataFrame, city_name: str=None, column_name: str=None, category: str = "monthly"):
    if category == "monthly":
        result_df = calculate_gini_coefficients_monthly_data(df)
    else:
        result_df = calculate_gini_coefficients_daily_data(df, city_name, column_name)
    return result_df
