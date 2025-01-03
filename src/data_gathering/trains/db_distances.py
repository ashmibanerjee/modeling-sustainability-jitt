import pandas as pd
from geopy.geocoders import Nominatim
from db_routes import load_connections
import geopy.distance
import networkx as nx


def calc_distance(lat_1, lng_1, lat_2, lng_2):
    coords_1 = (lat_1, lng_1)
    coords_2 = (lat_2, lng_2)

    return geopy.distance.distance(coords_1, coords_2).km


def get_coordinates(place: str):
    # print(place)
    geolocator = Nominatim(user_agent="my_user_agent")
    try:
        location = geolocator.geocode(place)
        return location.latitude, location.longitude
    except AttributeError:
        print(f"Could not find coordinates for {place}")
        return None, None


def add_coords_to_stations():
    """
    Adds coordinates to the stations in the graphml file
    :return:
    """
    file_name = "../../../../data/trains_data/db_routes.graphml"
    G = load_connections(file_name)
    stations = list(G.nodes)
    places = []
    for station in stations:
        match station:
            case "Weilheim (Oberbay)":
                lat, lng = 47.84296642653065, 11.13624870341107
            case "Ottersberg (Han)":
                lat, lng = 53.09720472479556, 9.133140490931462
            case "Köln Messe/Deutz Gl.":
                lat, lng = 50.941147389145314, 6.974174048904589
            case "Rzeszow Gl.":
                lat, lng = 50.04314525141831, 22.005722078808063
            case "Przemysl Gl.":
                lat, lng = 49.78352393884691, 22.776367572397664
            case "Jesenice (SL)":
                lat, lng = 46.43639417594748, 14.054838493079426
            case "Zagreb Glavni Kolod.":
                lat, lng = 45.804655983858055, 15.978812198910079
            case "Maasbüll (b Niebüll)":
                lat, lng = 54.75442982018756, 8.8127361430253
            case "Dagebüll Mole\r\nneg RB":
                lat, lng = 54.730121478494304, 8.690239853045648
            case "Emden Außenhafen\r\nRE":
                lat, lng = 53.34410045830314, 7.186083041827918
            case "Kolding st":
                lat, lng = 55.49080899961766, 9.481204989436652
            case "Odense st":
                lat, lng = 55.401214221428, 10.387771305411396
            case "Vac":
                lat, lng = 47.78275821356291, 19.13299804595499
            case "Tarnow":
                lat, lng = 50.00573190672661, 20.974487138319876
            case "Nyborg st":
                lat, lng = 55.31393585347483, 10.802619741345218
            case "Kuty":
                lat, lng = 48.66214848065675, 17.047201242224215
            case "Jaroslaw":
                lat, lng = 50.01089892084418, 22.67710512782239
            case _:
                lat, lng = get_coordinates(station)
        places.append([station, lat, lng])
    df = pd.DataFrame(places, columns=["station", "lat", "lng"])
    df.to_csv("../../../../data/trains_data/db_stations_with_coords.csv", index=False)


def add_distances_to_routes():
    """
    Adds distance to the routes in the graphml file
    :return:
    """
    graph_file_name = "../../../../data/trains_data/db_routes.graphml"
    G = load_connections(graph_file_name)
    routes = list(G.edges)

    lat_lng_df = pd.read_csv("../../../../data/trains_data/db_stations_with_coords.csv")
    lat_lng_df = lat_lng_df.set_index("station")
    debug_count = 0
    for route in routes:
        try:
            src = route[0]
            dest = route[1]
            src_lat = lat_lng_df.loc[src, "lat"]
            src_lng = lat_lng_df.loc[src, "lng"]

            dest_lat = lat_lng_df.loc[dest, "lat"]
            dest_lng = lat_lng_df.loc[dest, "lng"]

            distance = calc_distance(src_lat, src_lng, dest_lat, dest_lng)
            G[src][dest]["distance_km"] = distance
        except (KeyError, ValueError):
            print(f"Could not find coordinates for {src} or {dest}")
            G[src][dest]["distance_km"] = 0
            debug_count += 1

    file_to_save = "../../../../data/trains_data/db_routes_with_distances.graphml"
    nx.write_graphml(G, file_to_save)
    print(
        "Graph computed with ",
        G.number_of_nodes(),
        " nodes and ",
        G.number_of_edges(),
        " edges",
    )
    print(f"Could not find coordinates for {debug_count} stations")


if __name__ == "__main__":
    #add_coords_to_stations()
    add_distances_to_routes()
