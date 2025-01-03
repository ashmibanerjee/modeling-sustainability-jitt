import pandas as pd

path_db_positions = "../../../../data/trains_data/db_stations_with_coords.csv"
path_input_df = "../../../../data/trains_data/df.xlsx"


def merge_positions(df_sections, file_path):
    stations = pd.read_csv(path_db_positions)
    stations = stations[["station", "lat", "lng"]]

    merged_df = df_sections.merge(
        stations, left_on="from", right_on="station", how="left"
    )
    merged_df = merged_df.merge(stations, left_on="to", right_on="station", how="left")

    merged_df.to_excel(file_path, index=False)


def get_sections():
    df = pd.read_excel(path_input_df)

    map_unidir = {}
    map_bidir = {}

    for index, row in df.iterrows():
        cur_pos = row["station"]
        next_pos = row["next_station"]

        if (
            str(cur_pos) != "nan"
            and str(next_pos) != "nan"
            and cur_pos != None
            and next_pos != None
        ):
            combi = (cur_pos, next_pos)
            combi_rev = (next_pos, cur_pos)

            if combi in map_unidir:
                map_unidir[combi] += 1
            else:
                map_unidir[combi] = 1

            if combi in map_bidir:
                map_bidir[combi] += 1
            else:
                if combi_rev in map_bidir:
                    map_bidir[combi_rev] += 1
                else:
                    map_bidir[combi] = 1

    print(len(map_unidir))
    print(len(map_bidir))

    # unidirectional
    data = []
    for (s1, s2), c in map_unidir.items():
        data.append({"from": s1, "to": s2, "count": c})

    df_uni = pd.DataFrame(data)

    # bidirectional
    data = []
    for (s1, s2), c in map_bidir.items():
        data.append({"from": s1, "to": s2, "count": c})

    df_bi = pd.DataFrame(data)
    return df_uni, df_bi


df_uni, df_bi = get_sections()
merge_positions(df_uni, "../../../../data/trains_data/sections_unidirectional.xlsx")
merge_positions(df_bi, "../../../../data/trains_data/sections_bidirectional.xlsx")
