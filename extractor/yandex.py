import requests

import extractor

class urls:
    def _build_tile_url(pano_id, zoom=0, x=0, y=0):
        """
        Build Yandex Tile URL.
        """
        zoom = 4 - int(zoom)
        url = f"https://pano.maps.yandex.net/{pano_id}/{zoom}.{x}.{y}"
        return url

    def _build_pano_url(lat, lng):
        """
        Build Yandex URL that returns panorama ID and metadata.
        """
        url = f"https://api-maps.yandex.ru/services/panoramas/1.x/?l=stv&lang=en_RU&ll={lng}%2C{lat}&origin=userAction&provider=streetview"
        return url

class misc:
    def get_pano_from_url(url):
        raise extractor.ServiceNotSupported

    def short_url(pano_id):
        raise extractor.ServiceNotSupported

class metadata:
    def get_date(pano_id) -> str:
        raise extractor.ServiceNotSupported

    def get_metadata(pano_id) -> str:
        raise extractor.ServiceNotSupported

    def get_coords(pano_id) -> float:
        raise extractor.ServiceNotSupported

def get_pano_id(lat, lon):
    url = urls._build_pano_url(lat, lon)
    data = requests.get(url).json()
    pano = data['data']['Data']['Images']['imageId']
    return {
        "pano_id": pano
    }

def get_max_zoom(pano):
    i = 0
    while True:
        url = urls._build_tile_url(pano, i)
        resp = requests.get(url)
        if resp.status_code != 200:
            return i
        else:
            i += 1
            continue

def _build_tile_arr(pano_id, zoom=2):
    x = 0
    y = 0
    x_axis = []
    y_axis = []

    # x axis
    while True:
        url = urls._build_tile_url(pano_id, zoom, x, y)
        r = requests.get(url).status_code
        match r:
            case 200:
                x_axis = x
                x += 1
            case _:
                x = 0
                break

    # y axis
    while True:
        url = urls._build_tile_url(pano_id, zoom, x, y)
        r = requests.get(url).status_code
        match r:
            case 200:
                y_axis = y
                y += 1
            case _:
                break

    arr = []
    for i in range(int(y_axis + 1)):
        arr.append([])

    # print(len(arr))
    for y in range(0, len(arr)):
        for x in range(x_axis + 1):
            url = urls._build_tile_url(pano_id, zoom, x, y)
            arr[y].append(url)
    return arr