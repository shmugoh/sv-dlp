from datetime import datetime
import re
import requests
import sv_dlp.services

class urls:
    def _build_tile_url(pano_id, zoom=0, x=0, y=0):
        """
        Build Yandex Tile URL.
        """
        url = f"https://pano.maps.yandex.net/{pano_id}/{zoom}.{x}.{y}"
        return url

    def _build_metadata_url(lat, lng, mode='ll'):
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
        # import urllib.parse
        # url = f'/?panorama%5Bpoint%5D=0%2C0&panorama%5Bid%5D={pano}'
        # return urllib.parse.quote(url)
        '''

class misc:
    def get_pano_from_url(url):
        url = requests.get(url).url
        try:
            pano = re.findall(r'5Bid%5D=(.+)&panorama%5Bpoint', url)[0]
            pano = metadata._get_pano_id(pano, '', 'oid')
        except IndexError:
            try:
                coords = re.findall(r'panorama%5Bpoint%5D=(.+)%2C(.+)', url)[0]
                lat, lng = coords[1], coords[0]
                pano = metadata._get_pano_id(lat, lng)
            except IndexError:
                raise sv_dlp.services.ServiceShortURLFound

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
    def _get_time(timestamp) -> datetime:
        date = datetime.fromtimestamp(int(timestamp))
        return date

    def get_metadata(pano_id=None, lat=None, lng=None, get_linked_panos=False) -> list:
        if pano_id == None:
            pano_id = metadata._get_pano_from_coords(lat, lng)
        raw_md = metadata._get_raw_metadata(pano_id)
        timeline = raw_md['data']['Annotation']['HistoricalPanoramas']

        img_size = raw_md['data']['Data']['Images']['Zooms'][0]
        md = {
            "service": "yandex",
            "pano_id": {
                "pano_id": raw_md['data']['Data']['panoramaId'], 
                "image_id": raw_md['data']['Data']['Images']['imageId']},
            "lat": raw_md['data']['Data']['Point']['coordinates'][0],
            "lng": raw_md['data']['Data']['Point']['coordinates'][1],
            "date": metadata._get_time(raw_md['data']['Data']['timestamp']), # to be used with datetime
            "size": [img_size['width'], img_size['height']],
            "max_zoom": len(raw_md['data']['Data']['Images']['Zooms']) - 1,
            "timeline": {}
        }
        for panorama in timeline:
            md = metadata._parse_panorama(md, panorama, output="timeline")
        if get_linked_panos:
            md['linked_panos'] = {}
            linked_panos = raw_md['data']['Annotation']['Graph']['Nodes']
            for panorama in linked_panos:
                if panorama['panoid'] == md['pano_id']['oid']: pass
                else: md = metadata._parse_panorama(md, panorama, output="linked_panos")
        return md
            
    def _parse_panorama(md, panorama_info, output=""):
        match output:
            case "timeline":
                md["timeline"].update(
                    {
                        "pano_id": {
                            "pano_id": panorama_info['Connection']['oid'], 
                            "image_id": None},
                        "date": metadata.get_time(panorama_info['timestamp'])
                    }
                )
            case "linked_panos":
                md["linked_panos"].update(
                    {
                        "pano_id": {
                            "pano_id": panorama_info['panoid'], 
                            "image_id": None},
                        "lat": panorama_info['lat'],
                        "lon": panorama_info['lon'],
                        "date": metadata.get_metadata(pano_id=panorama_info['panoid'])['date'] # def scrapping this later
                        # no way of getting date information, unless if
                        # get_metadata is called by each panorama, which would
                        # make it a bit slower
                    }
                )
            case _:
                raise Exception # lol
        return md

    def _get_raw_metadata(pano_id) -> list:
        url = urls._build_metadata_url(pano_id, 0, 'oid')
        print(url)
        data = requests.get(url).json()
        if data['status'] != 'success': raise sv_dlp.services.PanoIDInvalid
        return data

    def _get_pano_from_coords(lat, lon, mode='ll'):
        try:
            url = urls._build_metadata_url(lat, lon, mode)
            data = requests.get(url).json()
            return data['data']['Data']['panoramaId']
        except Exception:
            raise sv_dlp.services.NoPanoIDAvailable

    def get_gen(pano_id):
        raise sv_dlp.services.ServiceNotSupported

def _build_tile_arr(metadata, zoom=2):
    pano_id = metadata['pano_id']['image_id']
    max_zoom = metadata['max_zoom']
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