from datetime import datetime
from pprint import pprint
import math
import sv_dlp.services
import requests
import json as j
import re
from random import choice
import urllib.parse

class urls:
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
    def _build_tile_url(pano_id, zoom=3, x=0, y=0):
        """
        Build Google Street View Tile URL
        """
        url = f"https://streetviewpixels-pa.googleapis.com/v1/tile?cb_client=maps_sv.tactile&panoid={pano_id}&x={x}&y={y}&zoom={zoom}&nbt=1&fover=2"
        return url

    def _build_metadata_url(pano_id=None, lat=None, lng=None, mode='GetMetadata', radius=500):
        '''
        Build GeoPhotoService call URL from
        Pano ID that contains panorama key data 
        such as image size, location, coordinates,
        date and previous panoramas.
        '''
        xdc = "_xdc_._" + ''.join([y for x in range(6) if (y := choice(urls.chars)) is not None])
        match mode:
            case 'GetMetadata':
                url = f'https://maps.googleapis.com/maps/api/js/GeoPhotoService.GetMetadata?pb=!1m5!1sapiv3!5sUS!11m2!1m1!1b0!2m2!1sen!2sUS!3m3!1m2!1e2!2s{pano_id}!4m6!1e1!1e2!1e3!1e4!1e8!1e6&callback={xdc}'
            case 'SingleImageSearch':
                url = f"https://maps.googleapis.com/maps/api/js/GeoPhotoService.SingleImageSearch?pb=!1m5!1sapiv3!5sUS!11m2!1m1!1b0!2m4!1m2!3d{lat}!4d{lng}!2d{radius}!3m20!1m1!3b1!2m2!1sen!2sUS!9m1!1e2!11m12!1m3!1e2!2b1!3e2!1m3!1e3!2b1!3e2!1m3!1e10!2b1!3e2!4m6!1e1!1e2!1e3!1e4!1e8!1e6&callback={xdc}"
            case 'SatelliteZoom':
                x, y = geo._coordinate_to_tile(lat, lng)
                url = f"https://www.google.com/maps/photometa/ac/v1?pb=!1m1!1smaps_sv.tactile!6m3!1i{x}!2i{y}!3i17!8b1"
        return url

    def _build_short_url(pano_id) -> str:
        """
        Build API call URL that shorts an encoded URL.
        Useful for shortening panorama IDs.
        """
        encoded_input = f"https://www.google.com/maps/@?api=1&map_action=pano&pano={pano_id}"
        url = f'https://www.google.com/maps/rpc/shorturl?pb=!1s{urllib.parse.quote(encoded_input)}'
        return url
    
class geo:
    def _project(lat, lng, TILE_SIZE=256):
        siny = math.sin((lat * math.pi) / 180)
        siny = min(max(siny, -0.9999), 0.9999)
        x = TILE_SIZE * (0.5 + lng / 360),
        y = TILE_SIZE * (0.5 - math.log((1 + siny) / (1 - siny)) / (4 * math.pi)),
        return x[0], y[0]
    def _coordinate_to_tile(lat, lng, tile_size=256, zoom=17):
        x, y = geo._project(lat, lng)
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
        return pano_id[0]

    def short_url(pano_id):
        """
        Shorts panorama ID by using the
        share function found on Google Maps
        """
        url = urls._build_short_url(pano_id)
        json = j.loads(requests.get(url).content[5:])
        return json[0]

class metadata:
    _convert_date = lambda raw_date : datetime.strptime(raw_date, '%Y/%m')

    def get_metadata(pano_id=None, lat=None, lng=None, get_linked_panos=False) -> dict:
        if pano_id == None:
            pano_id = metadata._get_pano_from_coords(lat, lng)
        raw_md = metadata._get_raw_metadata(pano_id)
        try:
            lat, lng = raw_md[1][0][5][0][1][0][2], raw_md[1][0][5][0][1][0][3] 
            image_size = raw_md[1][0][2][2][0] # obtains highest resolution
            image_avail_res = raw_md[1][0][2][3] # obtains all resolutions available
            raw_image_date = raw_md[1][0][6][-1] # [0] for year - [1] for month
            raw_image_date = f"{raw_image_date[0]}/{raw_image_date[1]}"
            # def considering parsing this as a protocol buffer instead - this is too messy
        except IndexError:
            raise sv_dlp.services.PanoIDInvalid
        md = {
            "service": "google",
            "pano_id": pano_id,
            "lat": float(lat),
            "lng": float(lng),
            "date": metadata._convert_date(raw_image_date),
            "size": image_size,
            "max_zoom": len(image_avail_res[0])-1,
            "misc": {
                "is_trekker": len(raw_md[1][0][5][0][3][0][0][2]) > 3,
                "gen": metadata._get_gen(image_size)
            },
            "timeline": {},
        }
        if md['misc']['is_trekker']:
            md['misc']['trekker_id'] = raw_md[1][0][5][0][3][0][0][2][3][0]
        md = metadata._parse_panorama(md, raw_md, output="timeline")
        if get_linked_panos:
            md = metadata._parse_panorama(md, raw_md, output="linked_panos")
        return md

    def _parse_panorama(md, raw_md, output=""):
        linked_panos = raw_md[1][0][5][0][3][0]
        buff = []
        match output:
            case "timeline":
                for pano_info in raw_md[1][0][5][0][8]:
                    if pano_info == None: break
                    else:
                        raw_pano_info = linked_panos[pano_info[0]]
                        buff.append({
                            "pano_id": raw_pano_info[0][1],
                            "lat": raw_pano_info[2][0][-2],
                            "lng": raw_pano_info[2][0][-1],
                            "date": metadata._convert_date(f"{pano_info[1][0]}/{pano_info[1][1]}")
                        })
                md["timeline"] = buff
            case "linked_panos":
                md["linked_panos"] = {}
                for pano_info in linked_panos:
                    pano_id = pano_info[0][1]
                    if pano_id != raw_md[1][0][1][1]:
                        if pano_id not in [x['pano_id'] for x in md['timeline']]:
                            date = metadata.get_metadata(pano_id=pano_id)['date']
                            buff.append({
                                    "pano_id": pano_info[0][1],
                                    "lat": pano_info[2][0][-2],
                                    "lng": pano_info[2][0][-1],
                                    "date": date,
                            })
                md["linked_panos"] = buff
            case _:
                raise Exception # lol
        return md

    def _get_raw_metadata(pano_id) -> dict:
        '''
        Returns panorama ID metadata.
        '''
        url = urls._build_metadata_url(pano_id=pano_id, mode='GetMetadata')
        data = str(requests.get(url).content)[38:-3].replace('\\', '\\\\')
        raw_md = j.loads(data)
        return raw_md

    def _get_pano_from_coords(lat, lng, radius=500) -> dict:
        """
        Returns closest Google panorama ID to given parsed coordinates.
        """
        try:
            url = urls._build_metadata_url(lat=lat, lng=lng, mode='SingleImageSearch', radius=radius)
            json = requests.get(url).text
            if "Search returned no images." in json:
                print("[google]: Finding nearest panorama via satellite zoom...")
                url = urls._build_metadata_url(lat=lat, lng=lng, mode='SatelliteZoom')
                json = requests.get(url).text
                data = j.loads(json[4:])
                pano = data[1][1][0][0][0][1]
            else:
                data = re.findall(r'\[[0-9],"(.+?)"].+?,\[\[null,null,(.+?),(.+?)\]', json)
                pano = data[0][0]
        except TypeError:
            raise sv_dlp.services.NoPanoIDAvailable
        # pans = re.findall(r'\[[0-9],"(.+?)"].+?,\[\[null,null,(.+?),(.+?)\]', json)
        return pano

    def _get_gen(image_size):
        match image_size:
            case 1664: return "1"
            case 6656: return "2/3"
            case 8192: return "4"

def _build_tile_arr(md, zoom=2):
    pano_id = md['pano_id']
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