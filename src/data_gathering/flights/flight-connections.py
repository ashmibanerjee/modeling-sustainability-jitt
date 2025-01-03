from flight_scraper import scraper
import pandas as pd

CHUNK = 1000


def get_flight_connections():
    df = pd.read_csv("../../../data/connections/connections.csv")
    # df = df.sample(n=3)

    # df = df[:CHUNK]
    df = df.loc[df.index >= 249]

    print("data frame read")

    column_names = ['Source', 'Destination', 'Airline', 'Departure_Time', 'Arrival_Time', 'Duration', "number_of_stops",
                    'Stops_info', "CO2_emission"]

    final_df = None

    for index, row in df.iterrows():
        print(f"\n iteration: {index} from {row['airport_1']} to {row['airport_2']}")
        flight_data = scraper(row['airport_1'], row['airport_2'])
        print("flight scraped")
        if final_df is None:
            final_df = pd.DataFrame(flight_data, columns=column_names)
        else:
            final_df = pd.concat([final_df, pd.DataFrame(flight_data, columns=column_names)], ignore_index=True)
        print("flight data appended")
        final_df.to_csv(f'../data/flights_data/flights_{CHUNK}.csv', index=False, encoding='utf-8')
        print("flight data saved")


if __name__ == '__main__':
    get_flight_connections()
