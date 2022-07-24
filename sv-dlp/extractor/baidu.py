from random import randrange
import re

import requests
import json as j
from pprint import pprint

import extractor

class urls:
    def _build_tile_url(panoID, x, y, zoom=4):
        """
        Build Baidu Maps Tile URL.
        """
        url = f"https://mapsv0.bdimg.com/?udt=20200825&qt=pdata&sid={panoID}&pos={y}_{x}&z={zoom}"
        return url

    def _build_pano_url(lat, lon):
        """
        Build Baidu URL containing panorama ID from
        coordinates.
        """
        url = f"https://mapsv0.bdimg.com/?udt=20200825&qt=qsdata&x={lat}&y={lon}"
        return url

    def _build_metadata_url(panoID):
        """
        Build Baidu URL containing maximum zoom levels
        and older imagery.
        """
        url = f"https://mapsv0.bdimg.com/?udt=20200825&qt=sdata&sid={panoID}"
        return url

class misc:
    def get_pano_from_url(url):
        new_url = requests.get(url).url
        pano_id = re.findall('panoid=(.*)&panotype', new_url)
        return pano_id

    def short_url(pano_id):
        raise extractor.ServiceNotSupported

class metadata:
    def get_date(pano_id) -> str:
        raise extractor.ServiceNotSupported

    def get_metadata(pano_id) -> str:
        url = urls._build_metadata_url(pano_id)
        data = requests.get(url).json()
        pprint(data)

    def get_coords(pano_id) -> float:
        raise extractor.ServiceNotSupported

def get_pano_id(lat, lon):
    url = urls._build_pano_url(lat, lon)
    json = requests.get(url).json()
    pano_id = json["content"]["id"]
    return {
        "pano_id": pano_id
    }

def get_max_zoom(pano_id):
    """
    Finds maximum available zoom from given panorama ID.
    """
    url = urls._build_metadata_url(pano_id)
    json = requests.get(url).json()
    return json["content"][0]["ImgLayer"][-1]["ImgLevel"]

def _find_max_axis(pano_id, zoom):
    x = 0
    y = 0
    x_axis = []
    y_axis = []

    # x axis
    while True:
        url = urls._build_tile_url(pano_id, x, y, zoom)
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
        url = urls._build_tile_url(pano_id, x, y, zoom)
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

def _build_tile_arr(pano_id, zoom, axis_arr):
    arr = []
    for i in range(zoom - 1):
        arr.append([])
    print(arr)

    for y in range(0, len(arr)):
        for x in range(len(axis_arr['x']) + 1):
            url = urls._build_tile_url(pano_id, x, y, zoom)
            arr[y].append(url)
    return arr

# if __name__ == "__main__":
#    pano_id = get_pano_id(39.900139527145846, 116.3958936511099)
#    zoom = _get_max_zoom(pano_id)
#    axis = _find_max_axis(pano_id, zoom)
#    tile_arr = _build_tile_arr(pano_id, zoom, axis)
#    print(tile_arr)