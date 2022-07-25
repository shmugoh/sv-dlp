import re
import sys
import requests
import urllib.parse

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

    def _build_short_url(pano) -> str:
        """
        Build URL that shorts panorama
        from given OID.
        """
        url = f'https://yandex.com/maps/?panorama%5Bpoint%5D=0%2C0&panorama%5Bid%5D={pano}'
        return url

        ''' 
        Refer to Issue #5
        # url = f'/?panorama%5Bpoint%5D=0%2C0&panorama%5Bid%5D={pano}'
        # return urllib.parse.quote(url)
        '''

class misc:
    def get_pano_from_url(url):
        url = requests.get(url).url
        try:
            pano = re.findall(r'5Bid%5D=(.+)&panorama%5Bpoint', url)[0]
            pano = get_pano_id(pano, '', 'oid')
        except IndexError:
            try:
                coords = re.findall(r'panorama%5Bpoint%5D=(.+)%2C(.+)', url)[0]
                lat, lng = coords[1], coords[0]
                pano = get_pano_id(lat, lng)
            except IndexError:
                raise extractor.ServiceShortURLFound

        return pano

    def short_url(pano_id):
        try:
            pano_id = pano_id['oid']
        except TypeError:
            # if pano id already parsed
            pass
        url = urls._build_short_url(pano_id)
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
    def get_date(pano_id) -> str:
        data = metadata.get_metadata(pano_id)['data']['Annotation']['HistoricalPanoramas']
        try:
            pano_id = pano_id['oid']
        except TypeError: # pano id already parsed
            pass

        for i in data:
            if i['Connection']['oid'] == pano_id:
                return int(i['Connection']['name'])
        return None


    def get_metadata(pano_id) -> str:
        try:
            pano_id = pano_id['oid']
        except TypeError: # pano id already parsed
            pass

        url = urls._build_pano_url(pano_id, 0, 'oid')
        data = requests.get(url).json()
        return data

    def get_coords(pano_id) -> float:
        data = metadata.get_metadata(pano_id)['data']['Annotation']['HistoricalPanoramas']
        try:
            pano_id = pano_id['oid']
        except TypeError: # pano id already parsed
            pass

        for i in data:
            if i['Connection']['oid'] == pano_id:
                coords = i['Connection']['Point']['coordinates']
                lat = coords[1]
                lng = coords[0]
                return lat, lng
        return None

    def get_gen(pano_id):
        raise extractor.ServiceNotSupported

def get_pano_id(lat, lon, mode='ll'):
    try:
        url = urls._build_pano_url(lat, lon, mode)
        data = requests.get(url).json()
        return {
            "pano_id": data['data']['Data']['Images']['imageId'],
            "oid": data['data']['Data']['panoramaId']
        }
    except Exception:
        raise extractor.NoPanoIDAvailable

def get_max_zoom(pano):
    data = metadata.get_metadata(pano)
    zooms = data['data']['Data']['Images']['Zooms']
    return len(zooms) - 1

def _build_tile_arr(pano_id, zoom=2):
    max_zoom = get_max_zoom(pano_id)
    zoom = max_zoom - zoom

    try:
        pano_id = pano_id['pano_id']
    except TypeError: # pano id already parsed
        pano_id = get_pano_id(pano_id, 0, 'oid')['pano_id']

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