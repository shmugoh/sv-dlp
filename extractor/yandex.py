import re
import sys
import requests

import extractor

class urls:
    def _build_tile_url(pano_id, zoom=0, x=0, y=0):
        """
        Build Yandex Tile URL.
        """
        url = f"https://pano.maps.yandex.net/{pano_id}/{zoom}.{x}.{y}"
        return url

    def _build_pano_url(lat, lng, mode='ll'):
        """
        Build Yandex URL that returns panorama ID and metadata.

        Supported modes: ll and oid
        """
        # can also be used as the metadata url

        match mode:
            case 'll':
                url = f"https://api-maps.yandex.ru/services/panoramas/1.x/?l=stv&lang=en_RU&{mode}={lng}%2C{lat}&origin=userAction&provider=streetview"
            case 'oid':
                url = f"https://api-maps.yandex.ru/services/panoramas/1.x/?l=stv&lang=en_RU&{mode}={lat}&origin=userAction&provider=streetview"
        return url

class misc:
    def get_pano_from_url(url):
        url = requests.get(url).url
        try:
            express = re.findall(r'panorama%5Bpoint%5D=(.+)%2C(.+)&panorama', url)[0]
        except IndexError:
            raise extractor.ServiceShortURLFound

        lat, lng = express[1], express[0]
        pano_id = get_pano_id(lat, lng)
        return pano_id

    def short_url(pano_id):
        raise extractor.ServiceNotSupported

class metadata:
    def get_date(pano_id) -> str:
        data = metadata.get_metadata(pano_id)['data']['Annotation']['HistoricalPanoramas']
        for i in data:
            if i['Connection']['oid'] == pano_id['oid']:
                return int(i['Connection']['name'])
        return None


    def get_metadata(pano_id) -> str:
        pano_id = pano_id['oid']
        url = urls._build_pano_url(pano_id, 0, 'oid')
        data = requests.get(url).json()
        return data

    def get_coords(pano_id) -> float:
        data = metadata.get_metadata(pano_id)['data']['Annotation']['HistoricalPanoramas']
        for i in data:
            if i['Connection']['oid'] == pano_id['oid']:
                coords = i['Connection']['oid']['coordinates']
                lat = coords[1]
                lng = coords[0]
                return lat, lng
        return None

    def get_gen(pano_id):
        raise extractor.ServiceFuncNotSupported

def get_pano_id(lat, lon):
    url = urls._build_pano_url(lat, lon)
    data = requests.get(url).json()
    return {
        "pano_id": data['data']['Data']['Images']['imageId'],
        "oid": data['data']['Data']['panoramaId']
    }

def get_max_zoom(pano):
    data = metadata.get_metadata(pano)
    zooms = data['data']['Data']['Images']['Zooms']
    return len(zooms) - 1

def _build_tile_arr(pano_id, zoom=2):
    max_zoom = get_max_zoom(pano_id)
    zoom = max_zoom - zoom

    pano_id = pano_id["pano_id"]

    arr = []
    x_y = [0, 0]
    i = 0

    while True:
        if i >= 2:
            break

        if i == 0: url = urls._build_tile_url(pano_id, zoom, x_y[0], 0)
        else: url = urls._build_tile_url(pano_id, zoom, 0, x_y[1])

        r = requests.get(url).status_code
        match r:
            case 200:
                x_y[i] += 1
            case _:
                i += 1
                continue

    for y in range(int(x_y[1])):
        arr.append([])
        for x in range(x_y[0]):
            url = urls._build_tile_url(pano_id, zoom, x, y)
            arr[y].insert(x, url)
    return arr

# if __name__ == '__main__':
#     try:
#         x = misc.get_pano_from_url('https://yandex.com/maps/-/CCUBqKHekA')
#     except extractor.ServiceShortURLFound as e:
#         print(e.message)