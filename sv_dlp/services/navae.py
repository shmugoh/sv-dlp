from datetime import datetime
from pprint import pprint
import re
import requests
import sv_dlp.services
import sv_dlp.download

class urls:
    def _build_tile_url(pano_id, zoom=0, block="", x=0, y=0):
        """
        Build Navae Tile URL.
        """
        if zoom == 0:
            url = f"https://panorama.pstatic.net/image/{pano_id}/512/P"
        else:
            zoom_map = {0: "P", 1: "M", 2: "L"}
            zoom = zoom_map.get(zoom, "M")
            url = f"https://panorama.pstatic.net/image/{pano_id}/512/{zoom}/{block}/{x}/{y}"
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
        
        ''' 
        Refer to Issue #30
        # encoded_input = f'https://map.naver.com/v5/?p={pano},0,0,0,Float'
        # url = (
        #     https://me2do.naver.com/common/requestJsonpV2?" +
        #     "_callback=window.spi_774030659" +
        #     "&svcCode=0022" +
        #     f"&url={urllib.parse.quote(encoded_input)})
        # return url
        '''

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
    _convert_date = lambda raw_date : datetime.strptime(raw_date, "%Y-%m-%d %H:%M:%S.%f") if "." in raw_date else datetime.strptime(raw_date, "%Y-%m-%d %H:%M:%S")

    def get_metadata(pano_id=None, lat=None, lng=None, get_linked_panos=False) -> list:
        if pano_id == None:
            pano_id = metadata._get_pano_from_coords(lat, lng)
        
        raw_md = metadata._get_raw_metadata(pano_id, mode="metadata")['basic']
        raw_timeline = metadata._get_raw_metadata(pano_id, mode="timeline")
        # timeline is in separate page
        
        md = {
            "service": "navae",
            "pano_id": raw_md["id"],
            "lat": raw_md['latitude'],
            "lng": raw_md['longitude'],
            "date": metadata._convert_date(raw_md['photodate']),
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
                            "date": metadata._convert_date(pano_info[3])
                        }
                    )
                md['timeline'] = buff
            case "linked_panos":
                linked_panos = raw_md['links']
                for pano_info in linked_panos[1:]:
                    pano_id = pano_info[0]
                    linked_md = metadata.get_metadata(pano_id)
                    buff.append(
                        {
                            "pano_id": pano_info[0],
                            "lat": linked_md['lat'],
                            "lon": linked_md['lng'],
                            "date": linked_md['date']
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
        try:
            if data['status']: # ['status'] only appears if pano is invalid 
                raise sv_dlp.services.PanoIDInvalid
        except KeyError:
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
    pano_id = metadata['pano_id']

    if zoom == 0:
        url = urls._build_tile_url(pano_id=pano_id, zoom=0)
        arr = [[url]]
    else:
        x_y = [1, 1] # per block
        block_map = {0: 'l', 1: 'f', 2: 'r', 3: 'b', 4: 'd', 5: 'u'}
        i = 0
        
        while True:
            if i >= 2:
                break
            if i == 0: url = urls._build_tile_url(pano_id, zoom, block="l", x=x_y[0]+1, y=1)
            else: url = urls._build_tile_url(pano_id, zoom, block="l", x=1, y=x_y[1]+1)
            response = requests.get(url)
            match response.status_code:
                case 200:
                    x_y[i] += 1
                case _:
                    i += 1
                    continue
                    
        arr = [[] for _ in range(x_y[1])]
        for y in range(x_y[1]):
            for z in range(len(block_map)):
                for x in range(x_y[0]):
                    # url = f"Block: {block_map.get(z)} ({z}) X: {x + 1} Y: {y + 1}"
                    url = urls._build_tile_url(pano_id, zoom, block=block_map.get(z), x=x+1, y=y+1)
                    arr[y].append(url)
    return arr

if __name__ == '__main__':
    pano = "wC7zT2RszClsKfYvh4Zcfg"
    md = metadata.get_metadata(pano_id=pano, get_linked_panos=True)
    pprint(md, sort_dicts=False)