import pandas as pd
from scipy.stats import ttest_1samp


def calculate_correlation_coefficients(df1: pd.DataFrame, df2: pd.DataFrame, label_1: str, label_2: str):
    # Merge the two DataFrames on the 'city' column
    merged_df = pd.merge(df1, df2, on='city', suffixes=(f'_{label_1}', f'_{label_2}'))

    numeric_columns_bn = [f'{month}_{label_1}' for month in df1.columns if month != 'city']
    numeric_columns_avc = [f'{month}_{label_2}' for month in df2.columns if month != 'city']

    # Create an empty DataFrame to store correlation coefficients
    correlation_df = pd.DataFrame(index=numeric_columns_bn, columns=numeric_columns_avc)

    # Iterate over the months and calculate correlation coefficients
    for month_bn, month_avc in zip(numeric_columns_bn, numeric_columns_avc):
        correlation_coefficient = merged_df[[month_bn, month_avc]].corr().iloc[0, 1]
        correlation_df.loc[month_bn, month_avc] = correlation_coefficient

    return correlation_df


def calc_significance_correlation(df1: pd.DataFrame, df2: pd.DataFrame, label_1:str, label_2: str, alpha:float = 0.05):
    numeric_columns_bn = [f'{month}_{label_1}' for month in df1.columns if month != 'city']
    numeric_columns_avc = [f'{month}_{label_2}' for month in df2.columns if month != 'city']
    # Merge the two DataFrames on the 'city' column
    merged_df = pd.merge(df1, df2, on='city', suffixes=(f'_{label_1}', f'_{label_2}'))

    t_test_df = pd.DataFrame(index=numeric_columns_bn, columns=['t-statistic', 'p_value'])

    # Iterate over the months and perform t-tests
    for month_bn, month_avc in zip(numeric_columns_bn, numeric_columns_avc):
        t_statistic, p_value = ttest_1samp(merged_df[month_bn] - merged_df[month_avc], 0)
        t_test_df.loc[month_bn, 't-statistic'] = t_statistic
        t_test_df.loc[month_bn, 'p_value'] = p_value
    alpha = 0.05

    # Add a column 'result' based on the p-value check
    t_test_df['result'] = t_test_df['p_value'].apply(lambda p: 'Significant' if p < alpha else 'Not Significant')

    return t_test_df
