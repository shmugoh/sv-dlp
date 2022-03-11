
from random import randrange

import requests
import json as j

class urls:
    def _build_pano_url(panoID, lat, lon):
        """
        Builds Baidu URL that obtains pano ID from coords.
        """
        url = f"https://mapsv{randrange(0, 1)}.bdimg.com/?qt=qsdata&x={lat}&y={lon}"
        return url

    def _build_tile_url(panoID, x, y, zoom=4):
        """
        Builds Baidu Tile URL.
        """
        url = f"https://mapsv{randrange(0, 1)}.bdimg.com/?qt=pdata&sid={panoID}&pos={y}_{x}&z={zoom}"
        return url

    def _build_metadata_url(panoID):
        """
        Builds Baidu URL that returns maximum zoom levels
        and older imagery,
        """
        url = f"https://mapsv{randrange(0, 1)}.bdimg.com/?qt=sdata&sid={panoID}"
        return url

class baidu:
    def get_pano_id(lat, lon):
        url = urls._build_pano_url(lat, lon)
        json = requests.get(url).json()
        pano_id = json["content"]["id"]
        return pano_id

    def _get_max_zoom(pano_id):
        """
        Finds maximum available zoom from given panorama ID.
        """
        url = urls._build_metadata_url(pano_id)
        json = requests.get(url).json()
        return json["content"][0]["ImgLayer"][-1]["ImgLevel"]

    def _find_max_axis(pano_id, zoom) -> dict["x", "y"]:
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

    def _build_tile_arr(pano_id, zoom, axis_arr):
        arr = [] 
        for i in range(zoom):
            arr.append([])

        for y in range(0, int(axis_arr['y']) + 1):
            for x in range(axis_arr['x']):
                url = urls._build_sv_url(pano_id, zoom, x, y)
                arr[y].append(url)
        return arr

if __name__ == "__main__":
    pano_id = "jYxwHUdPuhm8NGfAH6y8IA"
    max_zoom = google._find_max_zoom(pano_id)
    half_zoom = max_zoom // 2
    print(urls._build_sv_url(pano_id, half_zoom))
    max_axis = google._find_max_axis(pano_id, half_zoom)
    tile_arr = google._build_tile_arr(pano_id, half_zoom, max_axis)
    print(tile_arr)
    print(len(tile_arr))