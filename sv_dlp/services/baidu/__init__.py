import re
import requests
import sv_dlp.services
from . import geo
import urllib.parse
from datetime import datetime

class urls:
    def _build_tile_url(pano_id, x, y, zoom=4):
        """
        Build Baidu Maps Tile URL.
        """
        url = f"https://mapsv0.bdimg.com/?udt=20200825&qt=pdata&sid={pano_id}&pos={y}_{x}&z={zoom}"
        return url

    def _build_pano_url(lng, lat):
        """
        Build Baidu URL containing panorama ID from
        coordinates.
        """
        url = f"https://mapsv0.bdimg.com/?udt=20200825&qt=qsdata&x={lng}&y={lat}"
        return url

    def _build_metadata_url(pano_id):
        """
        Build Baidu URL containing maximum zoom levels
        and older imagery.
        """
        url = f"https://mapsv0.bdimg.com/?udt=20200825&qt=sdata&sid={pano_id}"
        return url

    def _build_short_url(pano_id, heading=0, pitch=0):
        encoded_input = f"https://map.baidu.com/?newmap=1&shareurl=1&panoid={pano_id}&panotype=street&heading={heading}&pitch={pitch}"
        url = f"https://j.map.baidu.com/?url={urllib.parse.quote(encoded_input)}"
        return url

class misc:
    def get_pano_from_url(url):
        new_url = requests.get(url).url
        pano_id = re.findall('panoid=(.*)&panotype', new_url)
        return pano_id[0]

    def short_url(pano_id):
        resp = requests.get(urls._build_short_url(pano_id))
        return resp.json()['url']

class metadata:
    def get_metadata(pano_id=None, lat=None, lng=None, get_linked_panos=False) -> list:
        if pano_id == None:
            pano_id = metadata._get_pano_from_coords(lat, lng)
        elif type(pano_id) is list:
            pano_id = pano_id[0]
        raw_md = metadata._get_raw_metadata(pano_id)
        ChangeCoord = geo.ChangeCoord()
        lng, lat = str(raw_md['content'][0]['RX']), str(raw_md['content'][0]['RY'])
        lng, lat = ChangeCoord.bd09mc_to_wgs84(lng, lat)
        
        md = sv_dlp.services.MetadataStructure(
            service="baidu",
            pano_id=raw_md["content"][0]["ID"],
            lat=lat,
            lng=lng,
            date=datetime.strptime(raw_md['content'][0]['Date'], '%Y%m%d'),
            max_zoom=raw_md["content"][0]["ImgLayer"][-1]["ImgLevel"] + 1
            )
        md = metadata._parse_panorama(md, raw_md, output="timeline")
        if get_linked_panos:
            md = metadata._parse_panorama(md, raw_md, output="linked_panos")
        return md

    def _parse_panorama(md, raw_md, output=""):
        buff = []
        match output:
            case "timeline":
                timeline = raw_md["content"][0]["TimeLine"][1:] # first iteration
                for pano_info in timeline:                       # is current panorama
                    buff.append(
                        {
                            "pano_id": pano_info["ID"],
                            "date": datetime.strptime(pano_info['TimeLine'], '%Y%m'),
                        }
                    )
                md.timeline = buff
            case "linked_panos":
                ChangeCoord = geo.ChangeCoord()
                linked_panos = raw_md['content'][0]['Roads'][0]['Panos']
                for pano_info in linked_panos:
                    lng, lat = str(pano_info['X']), str(pano_info['Y'])
                    lng, lat = ChangeCoord.bd09mc_to_wgs84(lng, lat)
                    buff.append(
                        {
                            "pano_id": pano_info["PID"],
                            "lat": lat,
                            "lon": lng,
                            "date": metadata.get_metadata(pano_id=pano_info['PID'])['date']
                            # no way of getting date information, unless if
                            # get_metadata is called by each panorama, which would
                            # make it a bit slower
                        }
                    )
                md.linked_panos = buff
            case _:
                raise Exception # lol
        return md

    def _get_raw_metadata(pano_id) -> str:
        url = urls._build_metadata_url(pano_id)
        data = requests.get(url).json()
        return data

    def _get_pano_from_coords(lat, lng):
        ChangeCoord = geo.ChangeCoord()
        lng, lat = ChangeCoord.wgs84_to_bd09(lng, lat)
        lng, lat = ChangeCoord.bd09_to_bd09mc(lng, lat)
        url = urls._build_pano_url(lng, lat)

        try:
            json = requests.get(url).json()
            pano_id = json["content"]["id"]
        except KeyError:
            raise sv_dlp.services.NoPanoIDAvailable
        return pano_id

def _build_tile_arr(metadata, zoom):
    pano_id = metadata['pano_id']
    arr = []
    x_y = [0, 0]
    i = 0

    while True:
        if i >= 2:
            break
        if i == 0: url = urls._build_tile_url(pano_id, x_y[0], 0, zoom)
        else: url = urls._build_tile_url(pano_id, 0, x_y[1], zoom)
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
            url = urls._build_tile_url(pano_id, x, y, zoom)
            arr[y].insert(x, url)
    return arr

# if __name__ == "__main__":
#    pano_id = get_pano_id(39.900139527145846, 116.3958936511099)
#    zoom = _get_max_zoom(pano_id)
#    axis = _find_max_axis(pano_id, zoom)
#    tile_arr = _build_tile_arr(pano_id, zoom, axis)
#    print(tile_arr)