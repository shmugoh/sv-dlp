from datetime import datetime
import re
import requests
import sv_dlp.services

class urls:
    def _build_tile_url(pano_id, zoom=0, x=0, y=0):
        """
        Build Navae Tile URL.
        """
        
        url = f"https://panorama.pstatic.net/image/{pano_id}/512/L/l/{x}/{y}"
        '''
        seems like 0 equals to 4 in all axes,
        therefore must start from 1
        
        Zooms:
        P - Full Low-Res Pano; does not require zoom 
        M - Medium
        L - Large
        
        6 blocks
        /L/l/ = 1
        /L/f/ = 2
        /L/r/ = 3
        /L/b/ = 4
        /L/d/ = 5
        /L/u/ = 6
        
        https://panorama.pstatic.net/image/wC7zT2RszClsKfYvh4Zcfg/512/P
        https://panorama.pstatic.net/image/wC7zT2RszClsKfYvh4Zcfg/512/L/l/3/2
        '''
        
        match zoom:
            case 0:
                zoom = "P"
            case 1:
                zoom = "M"
            case 2:
                zoom = "L"
        # just to have an idea
        
        return url

    def _build_metadata_url(pano_id=None, lat=None, lng=None, mode='coords') -> str:
        """
        Build Navae URL that returns panorama ID and metadata.
        """
        match mode:
            case 'coords':
                url = f"https://map.naver.com/v5/api/v2/nearby/{lng}/{lat}/3"
            case 'pano':
                url = f"https://panorama.map.naver.com/metadata/basic/{pano_id}?lang=en"
            case 'timeline':
                url = f"https://panorama.map.naver.com/metadata/timeline/{pano_id}"
        return url

    def _build_short_url(pano) -> str:
        """
        Build URL that shorts panorama
        from given Panorama ID.
        """
        encoded_input = f'https://map.naver.com/v5/?p={pano},0,0,0,Float'        
        return encoded_input
        
        # url = f'https://me2do.naver.com/common/requestJsonpV2?_callback=window.spi_774030659&svcCode=0022&url={urllib.parse.quote(encoded_input)}'
        # return url

class misc:
    def get_pano_from_url(url):
        # https://naver.me/5nPJ8YmO
        # https://map.naver.com/v5/?c=15.71,0,0,1,dh&p=SYL0YBLy6kvNTQfTsvXjeg,4.53,3.89,47.75,Float
        url = requests.get(url).url
        pano = re.findall(r'p=(\w+)', url)
        return pano

    def short_url(pano_id):
        url = urls._build_short_url(pano_id)
        return url


class metadata:
    # https://codebeautify.org/jsonviewer/y2325fba3

    def get_metadata(pano_id=None, lat=None, lng=None, get_linked_panos=False) -> list:
        if pano_id == None:
            pano_id = metadata._get_pano_from_coords(lat, lng)
        
        raw_md = metadata._get_raw_metadata(pano_id)['basic']
        raw_timeline = metadata._get_raw_metadata(pano_id)
        # timeline is in separate page
        
        md = {
            "service": "navae",
            "pano_id": raw_md["id"],
            "lat": raw_md['latitude'],
            "lng": raw_md['longitude'],
            "date": raw_md['photodate'], # must parse it to datetime
            "size": None,   # raw_md['image'] has tile_size and segment
            "max_zoom": 2,  # maybe i'll include it idk
            "timeline": {}
        }
        md = metadata._parse_panorama(md, raw_timeline, output="timeline") 
        if get_linked_panos:
            md = metadata._parse_panorama(md, raw_md, output="linked_panos")
        return md
            
    def _parse_panorama(md, raw_md, output=""):
        buff = []
        match output:
            case "timeline":
                timeline = raw_md['timeline']['panoramas']
                for pano_info in timeline[1:]:
                    buff.append(
                        {
                            "pano_id": pano_info[0],
                            "date": pano_info[3]
                        }
                    )
                md['timeline'] = buff
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
                md['linked_panos'] = buff
            case _:
                raise Exception # lol
        return md

    def _get_raw_metadata(pano_id, mode="metadata") -> list:
        match mode:
            case "metadata":
                url = urls._build_metadata_url(pano_id=pano_id, mode='pano')
            case "timeline":
                url = urls._build_metadata_url(pano_id=pano_id, mode='timeline')
        resp = requests.get(url)
        data = resp.json()
        if data['status']: # ['status'] only appears if pano is invalid 
            raise sv_dlp.services.PanoIDInvalid
        return data

    def _get_pano_from_coords(lat, lon):
        try:
            url = urls._build_metadata_url(lat=lat, lng=lon, mode='coords')
            data = requests.get(url).json()
            return data['features'][0]['properties']['id']
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