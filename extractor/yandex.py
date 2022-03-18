import requests

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

def get_pano_id(lat, lon):
    url = urls._build_pano_url(lat, lon)
    data = requests.get(url).json()
    pano = data['data']['Data']['Images']['imageId']
    return {
        "pano_id": pano
    }

def _find_max_axis(pano_id, zoom=2):
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

    max_axis = {
        "x": x_axis,
        "y": y_axis
    }
    return max_axis

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

def _build_tile_arr(pano_id, zoom, axis_arr):
    arr = []
    for i in range(int(axis_arr['y']) + 1):
        arr.append([])

    # print(len(arr))
    for y in range(0, len(arr)):
        for x in range(axis_arr['x'] + 1):
            url = urls._build_tile_url(pano_id, zoom, x, y)
            arr[y].append(url)
    return arr
