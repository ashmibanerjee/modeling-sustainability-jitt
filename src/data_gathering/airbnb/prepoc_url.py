import pandas as pd
import requests

def preproc():
    import pandas as pd

    # City-country mapping
    city_country_mapping = {
        'Amsterdam': 'The Netherlands',
        'Antwerp': 'Belgium',
        'Athens': 'Greece',
        'Barcelona': 'Spain',
        'Bergamo': 'Italy',
        'Berlin': 'Germany',
        'Bologna': 'Italy',
        'Bordeaux': 'France',
        'Brussels': 'Belgium',
        'Copenhagen': 'Denmark',
        'Crete': 'Greece',
        'Edinburgh': 'United Kingdom',
        'Euskadi': 'Spain',
        'Florence': 'Italy',
        'Geneva': 'Switzerland',
        'Ghent': 'Belgium',
        'Girona': 'Spain',
        'Greater Manchester': 'United Kingdom',
        'Istanbul': 'Turkey',
        'Lisbon': 'Portugal',
        'London': 'United Kingdom',
        'Lyon': 'France',
        'Madrid': 'Spain',
        'Malaga': 'Spain',
        'Mallorca': 'Spain',
        'Menorca': 'Spain',
        'Milan': 'Italy',
        'Munich': 'Germany',
        'Naples': 'Italy',
        'Paris': 'France',
        'Pays Basque': 'France',
        'Prague': 'Czech Republic',
        'Puglia': 'Italy',
        'Riga': 'Latvia',
        'Rome': 'Italy',
        'Rotterdam': 'Netherlands',
        'Sevilla': 'Spain',
        'Sicily': 'Italy',
        'South Aegean': 'Greece',
        'Stockholm': 'Sweden',
        'The Hague': 'Netherlands',
        'Thessaloniki': 'Greece',
        'Trentino': 'Italy',
        'Valencia': 'Spain',
        'Venice': 'Italy',
        'Vienna': 'Austria',
        'Zurich': 'Switzerland',
        'Dublin': 'Ireland',
        'Malta': 'Malta'
    }

    # Creating DataFrame
    df_city_country = pd.DataFrame(list(city_country_mapping.items()), columns=['city', 'country'])
    df_city_country.to_csv("../../../data/airbnb_data/airbnb_city_country_mapping.csv", index=False)
