import requests
from geocoding import geocoding


url = "https://api.opentripmap.com/0.1/ru"
API_KEY = "5ae2e3f221c38a28845f05b608ecf7df2342682bfe8bba4f040ebdff"


def get_object_list(lat: float, lon: float, radius: float = 1000, limit: int = 1):
    query = {
        'lat': str(lat),
        'lon': str(lon),
        'radius': str(radius),
        'limit': str(limit),
        'lang': 'ru',
        'apikey': API_KEY
    }
    return requests.get(url + "/places/radius", params=query).json()


def get_object_properties(xid: str):
    return requests.get(url + "/places/xid/" + xid, params={'apikey': API_KEY}).json()


if __name__ == "__main__":
    answer = geocoding("Цветной проезд, Академгородок")
    point = answer['hits'][0]['point']
    places = get_object_list(point['lat'], point['lng'])
    print(places)
    # print("Достопримечательности  Академгородка:")
    # for feature in places['features']:
    #     print(feature['properties']['name'])
