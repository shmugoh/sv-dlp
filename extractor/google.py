import requests
import xmltodict
import json as j

import re
from random import randrange

class urls:
    def _build_sv_url(pano_id, zoom=3, x=0, y=0):
        """
        Builds Google Street View Tile URL
        """
        url = f"https://streetviewpixels-pa.googleapis.com/v1/tile?cb_client=maps_sv.tactile&panoid={pano_id}&x={x}&y={y}&zoom={zoom}&nbt=1&fover=2"
        return url

    def _build_photometa_url(lat, lon):
        """
        Builds Google URL. Includes panorama ID and imagery date
        """
        url = f"https://www.google.com/maps/photometa/si/v1?pb=!1m4!1smaps_sv.tactile!11m2!2m1!1b1!2m4!1m2!3d{lat}!4d{lon}!2d50!3m17!1m2!1m1!1e2!2m2!1ses-419!2sco!9m1!1e2!11m8!1m3!1e2!2b1!3e2!1m3!1e3!2b1!3e2!4m57!1e1!1e2!1e3!1e4!1e5!1e6!1e8!1e12!2m1!1e1!4m1!1i48!5m1!1e1!5m1!1e2!6m1!1e1!6m1!1e2!9m36!1m3!1e2!2b1!3e2!1m3!1e2!2b0!3e3!1m3!1e3!2b1!3e2!1m3!1e3!2b0!3e3!1m3!1e8!2b0!3e3!1m3!1e1!2b0!3e3!1m3!1e4!2b0!3e3!1m3!1e10!2b1!3e2!1m3!1e10!2b0!3e3"
        return url

    def _build_geophoto_meta_url(pano_id):
        """
        Builds Google Maps API URL. Useful for metadata related stuff.
        """
        url = f'https://maps.googleapis.com/maps/api/js/GeoPhotoService.GetMetadata?pb=!1m5!1sapiv3!5sUS!11m2!1m1!1b0!2m2!1sen!2sUS!3m3!1m2!1e2!2s{pano_id}!4m6!1e1!1e2!1e3!1e4!1e8!1e6&callback=a'
        return url

    def _build_short_url(pano_id) -> str:
        """
        Builds API call URL that shorts an encoded URL.
        Useful for shortening panorama IDs. 
        """
        encoded_input = f"https%3A%2F%2Fwww.google.com%2Fmaps%2F%40%3Fapi%3D1%26map_action%3Dpano%26pano%3D{pano_id}" # trynna make it modular
        url = f'https://www.google.com/maps/rpc/shorturl?pb=!1s{encoded_input}'
        return url

    def _build_cbk_url(pano_id) -> str:
        '''
        Builds Google CBK url that returns panorama
        key data such as image data, coordinates,
        zoom levels, maximum image size, etc.
        '''
        i = randrange(0, 3)
        url = f'https://cbk{i}.google.com/cbk?output=xml&panoid={pano_id}'
        return url

class google:
    def _cbk_to_dict(url: str) -> dict:
        '''
        Turns CBK to a Python Dictionary format, as
        the CBK call is outputed in a XML format.

        Automatically does a GET request, so no need
        to parse one.
        '''
        cbk_xml = requests.get(url).content
        cbk_dict = xmltodict.parse(cbk_xml)
        return cbk_dict

    def get_pano_id(lat, lon) -> dict:
        """
        Returns closest Google panorama ID to given parsed coordinates.
        """

        url = urls._build_photometa_url(lat, lon)
        json = requests.get(url).text
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

    def _find_max_zoom(pano_id):
        """
        Finds maximum available zoom from given panorama ID.
        """
        url = urls._build_cbk_url(pano_id)
        data = google._cbk_to_dict(url)
        return int(data['panorama']['data_properties']['@num_zoom_levels'])

    def _find_max_axis(pano_id, zoom) -> dict["x", "y"]:
        x = 0
        y = 0
        x_axis = []
        y_axis = []

        # x axis
        while True:
            url = urls._build_sv_url(pano_id, zoom, x, y)
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
            url = urls._build_sv_url(pano_id, zoom, x, y)
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
        for i in range(int(axis_arr['y']) + 1):
            arr.append([])

        # print(len(arr))
        for y in range(0, len(arr)):
            for x in range(axis_arr['x']):
                url = urls._build_sv_url(pano_id, zoom, x, y)
                arr[y].append(url)
        return arr

    def is_trekker(pano_id) -> bool:
        """
        Returns if given panorama ID is
        trekker or not. Might be useful
        with the planned generator.

        Thank you nur#2584 for guiding me out.
        """
        url = urls._build_geophoto_meta_url(pano_id)
        json = j.loads(requests.get(url).content[12:-2])
        return len(json[1][0][5][0][3][0][0][2]) > 3

    def short_url(pano_id):
        """
        Shorts panorama ID by using the 
        share function found on Google Maps
        """
        url = urls._build_short_url(pano_id)
        json = j.loads(json = j.loads(requests.get(url).content[5:]))
        return json[0]


if __name__ == "__main__":
    print(urls._build_photometa_url(50.95475387573242,6.971647262573242))
    # pano_id = "jYxwHUdPuhm8NGfAH6y8IA"
    # max_zoom = google._find_max_zoom(pano_id)
    # half_zoom = max_zoom // 2
    # print(urls._build_sv_url(pano_id, half_zoom))
    # max_axis = google._find_max_axis(pano_id, half_zoom)
    # tile_arr = google._build_tile_arr(pano_id, half_zoom, max_axis)
    # print(tile_arr)
    # print(len(tile_arr))