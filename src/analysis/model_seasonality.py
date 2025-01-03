import pandas as pd
import glob
import os
from scipy.stats import pearsonr, spearmanr, kendalltau
from sklearn.linear_model import LinearRegression
from sklearn import metrics
from sklearn.model_selection import train_test_split


def calc_correlation_coefficients(x:list, y:list):
    pearson, _ = pearsonr(x, y)
    spearman, _ = spearmanr(x, y)
    kendall, _ = kendalltau(x, y)
    return pearson, spearman, kendall


def compute_linear_regression(X, y):
    X = X.values.reshape(-1, 1)
    y = y.values.flatten()

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

    # Create linear regression model
    model = LinearRegression()

    # Fit the model to the training data
    model.fit(X_train, y_train)

    # Make predictions on the test set
    y_pred = model.predict(X_test)

    # Print results
    print(f'Linear Regression Coefficient: {model.coef_[0]}')
    print(f'Linear Regression Intercept: {model.intercept_}')
    mae = metrics.mean_absolute_error(y_test, y_pred)
    mse = metrics.mean_squared_error(y_test, y_pred)
    return mae, mse


def calc_correlations_for_cities(inhalt_label="APREF"):
    city_files = [os.path.basename(x).split(".")[0] for x in glob.glob(f"../../plots_data/seasonality/airbnb_x_tourmis/*_{inhalt_label}.csv")]
    pearson_list = []
    spearman_list = []
    kendall_list = []
    maes = []
    mses = []
    file_to_save = f"../../plots_data/seasonality/city_correlations_airbnb_tourmis_{inhalt_label}.csv"
    column_names = ["city", "pearson", "spearman", "kendall", "lin_reg_mae", "lin_reg_mse"]
    city_names  = [x.split("_")[0] for x in city_files]
    for city_file in city_files:
        df = pd.read_csv(f"../../plots_data/seasonality/airbnb_x_tourmis/{city_file}.csv")
        x = df["avg_listing_price_normalized"].tolist()
        column_name = f"normalized_{inhalt_label}_2022"
        y = df[column_name].tolist()
        pearson, spearman, kendall = calc_correlation_coefficients(x, y)
        pearson_list.append(pearson)
        spearman_list.append(spearman)
        kendall_list.append(kendall)
        mae, mse = compute_linear_regression(df["avg_listing_price_normalized"], df[column_name])
        maes.append(mae)
        mses.append(mse)
        print(f"Done for {city_file}")
    df_corr = pd.DataFrame(list(zip(city_names, pearson_list, spearman_list, kendall_list, maes, mses)), columns=column_names)
    df_corr = df_corr.sort_values(by=["city"]).reset_index(drop=True)
    df_corr.to_csv(file_to_save, index=False)


if __name__ == "__main__":
    INHALT_LABELS = ["APREF", "NPREF"]
    for inhalt_label in INHALT_LABELS:
        calc_correlations_for_cities(inhalt_label=inhalt_label)
