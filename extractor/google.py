import requests
import json as j

import re
from random import randrange

class urls:
    def _build_tile_url(pano_id, zoom=3, x=0, y=0):
        """
        Build Google Street View Tile URL
        """
        url = f"https://streetviewpixels-pa.googleapis.com/v1/tile?cb_client=maps_sv.tactile&panoid={pano_id}&x={x}&y={y}&zoom={zoom}&nbt=1&fover=2"
        return url

    def _build_pano_url(lat, lon):
        """
        Build Google URL containing panorama ID and imagery date
        from coordinates.
        """
        url = f"https://maps.googleapis.com/maps/api/js/GeoPhotoService.SingleImageSearch?pb=!1m5!1sapiv3!5sUS!11m2!1m1!1b0!2m4!1m2!3d{lat}!4d{lon}!2d50!3m18!2m2!1sen!2sUS!9m1!1e2!11m12!1m3!1e2!2b1!3e2!1m3!1e3!2b1!3e2!1m3!1e10!2b1!3e2!4m6!1e1!1e2!1e3!1e4!1e8!1e6&callback=_xdc_._clm717"
        return url

    def _build_metadata_url(pano_id) -> str:
        '''
        Build Google CBK URL containing panorama
        key data such as image data, coordinates,
        zoom levels, maximum image size, etc.
        '''
        i = randrange(0, 3)
        url = f'https://cbk{i}.google.com/cbk?output=json&panoid={pano_id}'
        return url

    def _build_geophoto_meta_url(pano_id):
        """
        Build Google Maps API URL.
        Useful for metadata related stuff.
        """
        url = f'https://maps.googleapis.com/maps/api/js/GeoPhotoService.GetMetadata?pb=!1m5!1sapiv3!5sUS!11m2!1m1!1b0!2m2!1sen!2sUS!3m3!1m2!1e2!2s{pano_id}!4m6!1e1!1e2!1e3!1e4!1e8!1e6&callback=a'
        return url

    def _build_short_url(pano_id) -> str:
        """
        Build API call URL that shorts an encoded URL.
        Useful for shortening panorama IDs.
        """
        encoded_input = f"https%3A%2F%2Fwww.google.com%2Fmaps%2F%40%3Fapi%3D1%26map_action%3Dpano%26pano%3D{pano_id}" # trynna make it modular
        url = f'https://www.google.com/maps/rpc/shorturl?pb=!1s{encoded_input}'
        return url

class misc:
    def get_pano_from_url(url):
        url = requests.get(url).url
        pano_id = re.findall(r'1s(.+)!2e', url)
        return pano_id

    def short_url(pano_id):
        """
        Shorts panorama ID by using the
        share function found on Google Maps
        """
        url = urls._build_short_url(pano_id)
        json = j.loads(requests.get(url).content[5:])
        return json[0]

class metadata:
    def get_date(pano_id) -> str:
        '''
        Returns image date from
        CBK URL.
        '''
        url = urls._build_metadata_url(pano_id)
        data = requests.get(url).json()
        return data["Data"]["image_date"]

    def is_trekker(pano_id) -> bool:
        """
        Returns if given panorama ID is
        trekker or not. Might be useful
        with the planned generator.

        Thank you nur#2584 for guiding me out.
        """
        url = urls._build_metadata_url(pano_id)
        data = requests.get(url).json()
        data["Data"]["scene"] = 0

        if int(data["Data"]["scene"]) == 1:
            return True
        elif int(data["Data"]["imagery_type"]) == 5 or "level_id" in ["Location"]:
            return True
        else: return False

    def get_metadata(pano_id) -> str:
        '''
        Returns metadata from CBK url.
        '''
        url = urls._build_metadata_url(pano_id)
        data = requests.get(url).json()
        return data

    def get_coords(pano_id) -> float: # lul
        url = urls._build_metadata_url(pano_id)
        data = requests.get(url).json()
        return data["Location"]["lat"], data["Location"]["lng"]

    def get_gen(pano_id):
        url = urls._build_metadata_url(pano_id)
        data = requests.get(url).json()
        width, height =  data["Data"]["image_width"], data["Data"]["image_height"]

        match width, height:
            case "3328", "1664":
                return "1"
            case "13312", "6656":
                return "2/3"
            case "16384", "8192":
                return "4"

def get_pano_id(lat, lon) -> dict:
    """
    Returns closest Google panorama ID to given parsed coordinates.
    """

    url = urls._build_pano_url(lat, lon)
    json = requests.get(url).text
    # print(json)
    pans = re.findall(r'\[[0-9],"(.+?)"].+?,\[\[null,null,(.+?),(.+?)\]', json)
    # formatting should be changed soon
    pan = {
        "pano_id": pans[0][0],
        "lat": pans[0][1],
        "lon": pans[0][2]
    }
    # when implementing -F command, it shall return various pano ids with the date
    # though keep in mind duplicates should be fixed and removed
    return pan

def get_max_zoom(pano_id):
    """
    Finds maximum available zoom from given panorama ID.
    """
    url = urls._build_metadata_url(pano_id)
    data = requests.get(url).json()
    return int(data['Location']['zoomLevels'])

def _build_tile_arr(pano_id, zoom) -> dict["x", "y"]:
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
    for i in range(int(y_axis) + 1):
        arr.append([])
    for y in range(0, len(arr)):
        for x in range(x_axis + 1):
            url = urls._build_tile_url(pano_id, zoom, x, y)
            arr[y].append(url)
    return arr

# if __name__ == "__main__":
#     pano = 'fzJzOcJLZPq-_QPBJzl5Dg'
#     get