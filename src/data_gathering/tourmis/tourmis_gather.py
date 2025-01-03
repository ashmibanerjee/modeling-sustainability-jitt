from pathlib import Path
from config.constants import TOURMIS_USER_NAME
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import numpy as np

# URL to send the POST request to
URL = "https://www.tourmis.info/cgi-bin/tmcc.pl"
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November",
          "December"]


def get_response(city_abbr: str, inhalt_label: str = "AG") -> str | None:
    # Payload data
    payload = {
        "sprache": "TXE",
        "id": {TOURMIS_USER_NAME},
        "db": "ECT",
        "ttype": "monthly",
        "dezimal": 4,
        "tabelle": "ECM-M6",
        "zl": city_abbr,
        "inhalt": inhalt_label,
        "hkl": "ZZ",
        "vonjahr": 2022,
        "ausgabe": 0
    }

    # Send POST request
    response = requests.post(URL, data=payload)
    if response.status_code == 200:
        return response.text
    else:
        return None


def get_inhalt_labels():
    script_content = """
    <SCRIPT LANGUAGE="JavaScript">
        inhlabels = new Array();
        inhlabels['AD'] = "Arrivals of all visitors (tourists and day visitors) in city area only";
        inhlabels['ADS'] = "Arrivals of all visitors (tourists and day visitors) in greater city area";
        inhlabels['AZ'] = "Arrivals in all forms of accommodation incl. VFR in city area only";
        inhlabels['AZS'] = "Arrivals in all forms of accommodation incl. VFR in greater city area";
        inhlabels['AA'] = "Arrivals in all forms of paid accommodation in city area only";
        inhlabels['AAS'] = "Arrivals in all forms of paid accommodation in greater city area";
        inhlabels['AG'] = "Arrivals in hotels and similar establishments in city area only";
        inhlabels['AGS'] = "Arrivals in hotels and similar establishments in greater city area";
        inhlabels['NZ'] = "Bednights in all forms of accommodation incl. VFR in city area only";
        inhlabels['NZS'] = "Bednights in all forms of accommodation incl. VFR in greater city area";
        inhlabels['NA'] = "Bednights in all forms of paid accommodation in city area only";
        inhlabels['NAS'] = "Bednights in all forms of paid accommodation in greater city area";
        inhlabels['NG'] = "Bednights in hotels and similar establishments in city area only";
        inhlabels['NGS'] = "Bednights in hotels and similar establishments in greater city area";
        inhlabels['APREF'] = "Arrivals (preferred definition)";
        inhlabels['NPREF'] = "Bednights (preferred definition)";
        function chkinhalt(nr) {
            var z = nr;
            var inhexists = document.qform.inhalt;
            if (inhexists != null) {
                document.qform.inhalt.options.length = 0;
                for (var i in inhlabels) {
                    if ( typeof(zlinh[z + ":" + i]) !== 'undefined' ) {
                        document.qform.inhalt.options[document.qform.inhalt.options.length] = new Option(inhlabels[i], i);
                    }
                }
            }
        }
    </SCRIPT>
    """

    # Use regular expressions to extract inhlabels
    inhlabels_match = re.findall(r'inhlabels\[\'([^\']+)\'\]\s*=\s*"([^"]+)"', script_content)

    # Create a dictionary from the matches
    inhlabels_dict = dict(inhlabels_match)

    # # Print the extracted inhlabels
    # for key, value in inhlabels_dict.items():
    #     print(f"{key}: {value}")

    inhalt_labels = pd.DataFrame(inhlabels_dict.items(), columns=["label", "description"])
    inhalt_labels.to_csv("../../../data/tourmis_data/inhalt_labels.csv", index=False, encoding='utf-8')
    return list(inhlabels_dict.keys())


def parse_html(city_html, city_name, inhalt_label):
    soup = BeautifulSoup(city_html, 'html.parser')
    tab = soup.find("table", {"class": "stats"})
    data_rows = tab.find_all('tr')[6:18]
    data = {'Month': [], 'Value': []}
    for row in data_rows:
        columns = row.find_all('td', class_='white')
        month = columns[0].text.strip()
        value = columns[1].text.strip().replace(',', '')
        data['Month'].append(month)
        data['Value'].append(value)
    df = pd.DataFrame({"Month": data["Month"], city_name: data["Value"]})
    df_T = df.T
    df_T.reset_index(inplace=True)

    new_header = df_T.iloc[0]  # grab the first row for the header
    df_T = df_T[1:]  # take the data less the header row
    df_T.columns = new_header  # set the header row as the df header
    df_T.rename(columns={"Month": "city"}, inplace=True)
    df_T["inhalt_label"] = inhalt_label
    return df_T


def get_all_data():
    inhalt_labels = get_inhalt_labels()
    saved_file_name = "../../../data/tourmis_data/tourmis_data_seasonality_transposed_with_nans.csv"

    tourmis_cities = pd.read_csv("../../../data/tourmis_data/tourmis_cities.csv")

    # seasonality_df = pd.read_csv(saved_file_name)
    # seasonality_df = seasonality_df.loc[seasonality_df["city"] == "Antwerp"]

    final_df = None
    for idx, row in tourmis_cities.iterrows():
        label_idx = 0
        city_data = None
        while label_idx < len(inhalt_labels):
            print(f"Trying for {row['city']} with label {inhalt_labels[label_idx]} ")
            city_html = get_response(row["abbreviation"], inhalt_label=inhalt_labels[label_idx])
            city_data_label = parse_html(city_html, row["city"], inhalt_labels[label_idx])
            if city_data is None:
                city_data = city_data_label
            else:
                city_data = pd.concat([city_data, city_data_label], ignore_index=True, sort=False)
            label_idx += 1

        if final_df is None:
            final_df = city_data
        else:
            final_df = pd.concat([final_df, city_data], ignore_index=True, sort=False)
        final_df.to_csv("../../../data/tourmis_data/tourmis_data_seasonality_raw.csv", index=False,
                        encoding='utf-8')


if __name__ == '__main__':
    get_all_data()

