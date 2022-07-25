from datetime import date
from pprint import pprint
import math
import sys
import requests
import json as j
import re
from random import choice

class urls:
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
    def _build_tile_url(pano_id, zoom=3, x=0, y=0):
        """
        Build Google Street View Tile URL
        """
        url = f"https://streetviewpixels-pa.googleapis.com/v1/tile?cb_client=maps_sv.tactile&panoid={pano_id}&x={x}&y={y}&zoom={zoom}&nbt=1&fover=2"
        return url

    def _build_pano_url(lat, lng, mode='singleimagesearch', radius=500):
        """
        Build GeoPhotoService call URL from
        coordinates containing panorama ID and imagery date
        """
        xdc = "_xdc_._" + ''.join([y for x in range(6) if (y := choice(urls.chars)) is not None])
        match mode:
            case 'singleimagesearch':
                url = f"https://maps.googleapis.com/maps/api/js/GeoPhotoService.SingleImageSearch?pb=!1m5!1sapiv3!5sUS!11m2!1m1!1b0!2m4!1m2!3d{lat}!4d{lng}!2d{radius}!3m20!1m1!3b1!2m2!1sen!2sUS!9m1!1e2!11m12!1m3!1e2!2b1!3e2!1m3!1e3!2b1!3e2!1m3!1e10!2b1!3e2!4m6!1e1!1e2!1e3!1e4!1e8!1e6&callback={xdc}"
            case 'satellite':
                x, y = urls._coordinate_to_tile(lat, lng)
                url = f"https://www.google.com/maps/photometa/ac/v1?pb=!1m1!1smaps_sv.tactile!6m3!1i{x}!2i{y}!3i17!8b1"
        return url

    def _build_metadata_url(pano_id):
        '''
        Build GeoPhotoService call URL from
        Pano ID that contains panorama key data 
        such as image size, location, coordinates,
        date and previous panoramas.
        '''
        xdc = "_xdc_._" + ''.join([y for x in range(6) if (y := choice(urls.chars)) is not None])
        url = f'https://maps.googleapis.com/maps/api/js/GeoPhotoService.GetMetadata?pb=!1m5!1sapiv3!5sUS!11m2!1m1!1b0!2m2!1sen!2sUS!3m3!1m2!1e2!2s{pano_id}!4m6!1e1!1e2!1e3!1e4!1e8!1e6&callback={xdc}'
        return url

    def _build_short_url(pano_id) -> str:
        """
        Build API call URL that shorts an encoded URL.
        Useful for shortening panorama IDs.
        """
        encoded_input = f"https%3A%2F%2Fwww.google.com%2Fmaps%2F%40%3Fapi%3D1%26map_action%3Dpano%26pano%3D{pano_id}" # trynna make it modular
        url = f'https://www.google.com/maps/rpc/shorturl?pb=!1s{encoded_input}'
        return url
    
    def _project(lat, lng, TILE_SIZE=256):
        siny = math.sin((lat * math.pi) / 180)
        siny = min(max(siny, -0.9999), 0.9999)
        x = TILE_SIZE * (0.5 + lng / 360),
        y = TILE_SIZE * (0.5 - math.log((1 + siny) / (1 - siny)) / (4 * math.pi)),
        return x[0], y[0]
    def _coordinate_to_tile(lat, lng, tile_size=256, zoom=17):
        x, y = urls._project(lat, lng)
        zoom = 1 << zoom
        tile_x = math.floor((x * zoom) / tile_size)
        tile_y = math.floor((y * zoom) / tile_size)
        return tile_x, tile_y


class misc:
    def get_pano_from_url(url):
        url = requests.get(url).url
        pano_id = re.findall(r'1s(.+)!2e', url)
        if pano_id == []:
            # https://www.google.com/maps/@?api=1&map_action=pano&pano=p1yAMqbHsH7sgAGIJWwBpw&shorturl=1
            pano_id = re.findall(r'pano=(.+)&shorturl=1', url)
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
    def get_metadata(pano_id, lng=None) -> dict:
        '''
        Returns panorama ID metadata.
        '''
        url = urls._build_metadata_url(pano_id)
        data = str(requests.get(url).content)[38:-3].replace('\\', '\\\\')
        json = j.loads(data)

        lat, lng = json[1][0][5][0][1][0][2], json[1][0][5][0][1][0][3] 
        image_size = json[1][0][2][2][0] # obtains highest resolution
        image_avail_res = json[1][0][2][3] # obtains all resolutions available
        image_date = json[1][0][6][-1] # [0] for year - [1] for month

        # coords = re.search('\[\[null,null,(-?[0-9]+.[0-9]+),(-?[0-9]+.[0-9]+).+?', data)
        # image_size = re.search('\[[0-9],[0-9],\[(.+?),.+?\]', data).group(1)
        # image_zoom = re.search('\[[0-9],[0-9],\[.+?,.+?\],\[\[\[(\[.+?)\],null', data).group(1)
        # image_zoom = ("["*2) + image_zoom
        # image_date = re.search('\[*(......)\]\],\["https:', data).group(1)
#       pans = re.search('\[[0-9]+,"(.+?)"\],\[[0-9],[0-9],\[.+?,(.+?)\],.+?\[\[null,null,(-?[0-9]+.[0-9]+),(-?[0-9]+.[0-9]+).+?\[*(......)\]\],\["https:', data).group(5)

        metadata = {
            "panoid": pano_id,
            "lat": float(lat),
            "lng": float(lng),
            "date": f"{image_date[0]}/{image_date[1]}",
            "size": image_size,
            "max_zoom": len(image_avail_res[0])-1,
            "is_trekker": len(json[1][0][5][0][3][0][0][2]) > 3
            }

        del url, data, image_size, image_avail_res, image_date
        return metadata

    def get_date(pano_id) -> str:
        '''
        Returns image date from
        get_metadata()
        '''
        md = metadata.get_metadata(pano_id)
        return md["date"]

    def _is_trekker(pano_id) -> bool:
        """
        Returns if given panorama ID is
        trekker or not. Might be useful
        with the planned generator.

        Thank you nur#2584 for guiding me out.
        """
        md = metadata.get_metadata(pano_id)
        return md["is_trekker"]

    def get_coords(pano_id) -> float: # lul
        md = metadata.get_metadata(pano_id)
        return md["lat"], md["lng"]

    def get_gen(pano_id):
        md = metadata.get_metadata(pano_id)
        size = md["size"]
        match size:
            case 1664: return "1"
            case 6656: return "2/3"
            case 8192: return "4"

def get_pano_id(lat, lon, radius=500) -> dict:
    """
    Returns closest Google panorama ID to given parsed coordinates.
    """
    url = urls._build_pano_url(lat, lon, 'singleimagesearch', radius)
    json = requests.get(url).text
    if "Search returned no images." in json:
        print("[GOOGLE]: Finding nearest panorama via satellite zoom...")
        url = urls._build_pano_url(lat, lon, mode='satellite')
        json = requests.get(url).text
        data = j.loads(json[4:])
        pano = data[1][1][0][0][0][1]
        lat = data[1][1][0][0][2][0][2]
        lng = data[1][1][0][0][2][0][3]
    else:
        data = re.findall(r'\[[0-9],"(.+?)"].+?,\[\[null,null,(.+?),(.+?)\]', json)
        pano = data[0][0]
        lat = data[0][1]
        lng = data[0][2]
    # pans = re.findall(r'\[[0-9],"(.+?)"].+?,\[\[null,null,(.+?),(.+?)\]', json)
    # print(url)

    # formatting should be changed soon
    pan = {
        "pano_id": pano,
        "lat": lat,
        "lon": lng
    }
    # when implementing -F command, it shall return various pano ids with the date
    # though keep in mind duplicates should be fixed and removed
    return pan

def get_max_zoom(pano_id):
    """
    Finds maximum available zoom from given panorama ID.
    """
    md = metadata.get_metadata(pano_id)
    zoom = md['max_zoom']
    if zoom == 5: zoom -= 1
    return zoom

def _build_tile_arr(pano_id, zoom=2):
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

if __name__ == "__main__":
    pano = 'fzJzOcJLZPq-_QPBJzl5Dg'
    pprint(_build_tile_arr(pano, zoom=3))