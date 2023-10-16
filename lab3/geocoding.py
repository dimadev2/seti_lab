import requests


url = "https://graphhopper.com/api/1/geocode"
API_KEY = "16a300d3-2b99-4838-9924-8622873009f7"


def geocoding(q: str, limit=1) -> dict:
    query = {
        "q": q,
        "locale": "en",
        "limit": str(limit),
        "reverse": "false",
        "debug": "false",
        "provider": "default",
        "key": API_KEY
    }

    return requests.get(url, params=query).json()


if __name__ == "__main__":
    data = geocoding("Академгородок")
    print(data)
    # for answer in data['hits']:
    #     print(answer['name'], " ", answer['city'], " ", answer['state'])
