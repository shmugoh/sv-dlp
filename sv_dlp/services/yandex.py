from datetime import datetime
from pprint import pprint
import re
from socketserver import DatagramRequestHandler
import sys
import requests
import sv_dlp.services

class urls:
    def _build_tile_url(pano_id, zoom=0, x=0, y=0):
        """
        Build Yandex Tile URL.
        """
        url = f"https://pano.maps.yandex.net/{pano_id}/{zoom}.{x}.{y}"
        return url

    def _build_metadata_url(pano_id=None, lat=None, lng=None, mode='coords') -> str:
        """
        Build Yandex URL that returns panorama ID and metadata.

        Supported modes are 'coords' & 'pano' (must be OID)
        """
        # can also be used as the metadata url

        match mode:
            case 'coords':
                url = f"https://api-maps.yandex.ru/services/panoramas/1.x/?l=stv&lang=en_RU&ll={lng}%2C{lat}&origin=userAction&provider=streetview"
            case 'pano':
                url = f"https://api-maps.yandex.ru/services/panoramas/1.x/?l=stv&lang=en_RU&oid={pano_id}&origin=userAction&provider=streetview"
        return url

    def _build_short_url(pano, heading=0, pitch=0) -> str:
        """
        Build URL that shorts panorama
        from given Panorama ID (OID).
        """
        url = f'https://yandex.com/maps/?panorama%5Bpoint%5D=0%2C0&panorama%5Bid%5D={pano}&panorama%5Bdirection%5D={heading}%2C{pitch}'
        return url

        ''' 
        Refer to Issue #5
        # import urllib.parse
        # url = f'/?panorama%5Bpoint%5D=0%2C0&panorama%5Bid%5D={pano}'
        # return urllib.parse.quote(url)
        '''

class misc:
    def get_pano_from_url(url):
        url = requests.get(url).url
        try:
            pano = re.findall(r'panorama%5Bid%5D=(.+)&', url)
            pano = metadata.get_metadata(pano_id=pano).pano_id['pano_id']
        except IndexError:
            try:
                coords = re.findall(r'panorama%5Bpoint%5D=(.+)%2C(.+)&panorama', url)[0]
                lat, lng = coords[1], coords[0]
                pano = metadata.get_metadata(lat=lat, lng=lng)['pano_id']['pano_id']
            except IndexError:
                raise sv_dlp.services.ServiceShortURLFound

        return pano

    def short_url(pano_id, heading=0, pitch=0, zoom=0):
        try:
            pano_id = pano_id['pano_id']
        except TypeError:
            # if pano id already parsed
            pass
        url = urls._build_short_url(pano_id, heading=heading, pitch=pitch)
        return url

        ''' 
        Refer to Issue #5
        # path = urls._build_short_url(pano_id)
        # url = (
        #     "https://yandex.com/maps/api/shortenPath?" + 
        #     "ajax=1" + 
        #     "csrfToken=ec630cf510c7af543851c6fc698a9402bc9f3939%3A1658692300" + 
        #     f"path={path}" + 
        #     "s=566210619" + 
        #     "sessionId=1658692300780_640251")
        # resp = session.get(url)
        # return resp
        '''


class metadata:
    _convert_date = lambda raw_date : datetime.fromtimestamp(int(raw_date))

    def get_metadata(pano_id=None, lat=None, lng=None, get_linked_panos=False) -> list:
        if pano_id == None:
            pano_id = metadata._get_pano_from_coords(lat, lng)
        elif type(pano_id) is list:
            try:
                pano_id = pano_id['pano_id']
            except Exception: # if oid already in list
                pano_id = pano_id[0]
        
        raw_md = metadata._get_raw_metadata(pano_id)
        md = sv_dlp.services.MetadataStructure(
            service="yandex",
            pano_id={
                "pano_id": raw_md['data']['Data']['panoramaId'], 
                "image_id": raw_md['data']['Data']['Images']['imageId']},
            lat=raw_md['data']['Data']['Point']['coordinates'][1],
            lng=raw_md['data']['Data']['Point']['coordinates'][0],
            date=metadata._convert_date(raw_md['data']['Data']['timestamp']),
            size = raw_md['data']['Data']['Images']['Zooms'][0],
            max_zoom=len(raw_md['data']['Data']['Images']['Zooms']) - 1,
        )
        md = metadata._parse_panorama(md, raw_md, output="timeline")
        if get_linked_panos:
            md = metadata._parse_panorama(md, raw_md, output="linked_panos")
        return md
            
    def _parse_panorama(md, raw_md, output=""):
        buff = []
        match output:
            case "timeline":
                timeline = raw_md['data']['Annotation']['HistoricalPanoramas']
                for pano_info in timeline:
                    buff.append(
                        {
                            "pano_id": {
                                "pano_id": pano_info['Connection']['oid'], 
                                "image_id": None},
                            "date": metadata._convert_date(pano_info['timestamp'])
                        }
                    )
                md.timeline = buff
            case "linked_panos":
                linked_panos = raw_md['data']['Annotation']['Graph']['Nodes']
                for pano_info in linked_panos:
                    if pano_info['panoid'] == md['pano_id']['pano_id']: pass
                    date = metadata.get_metadata(pano_id=pano_info["panoid"])['date']
                    buff.append(
                        {
                            "pano_id": {
                                "pano_id": pano_info['panoid'], 
                                "image_id": None},
                            "lat": pano_info['lat'],
                            "lon": pano_info['lon'],
                            "date": date
                            # no way of getting date information, unless if
                            # get_metadata is called by each panorama, which would
                            # make it a bit slower
                        }
                )
                md.linked_panos = buff
            case _:
                raise Exception # lol
        return md

    def _get_raw_metadata(pano_id) -> list:
        url = urls._build_metadata_url(pano_id=pano_id, mode='pano')
        try:
            resp = requests.get(url)
            data = resp.json()
        except Exception as e:
            resp = requests.get(url)
            data = resp.json()
        if data['status'] != 'success': raise sv_dlp.services.PanoIDInvalid
        return data

    def _get_pano_from_coords(lat, lon):
        try:
            url = urls._build_metadata_url(lat=lat, lng=lon, mode='coords')
            data = requests.get(url).json()
            return data['data']['Data']['panoramaId']
        except Exception:
            raise sv_dlp.services.NoPanoIDAvailable

    def get_gen(pano_id):
        raise sv_dlp.services.ServiceNotSupported

def _build_tile_arr(metadata, zoom=2):
    pano_id = metadata.pano_id['image_id']
    max_zoom = metadata.max_zoom
    zoom = max_zoom - zoom

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