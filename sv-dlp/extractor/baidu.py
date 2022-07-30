import re
import requests
import extractor

class urls:
    def _build_tile_url(panoID, x, y, zoom=4):
        """
        Build Baidu Maps Tile URL.
        """
        url = f"https://mapsv0.bdimg.com/?udt=20200825&qt=pdata&sid={panoID}&pos={y}_{x}&z={zoom}"
        return url

    def _build_pano_url(lat, lon):
        """
        Build Baidu URL containing panorama ID from
        coordinates.
        """
        url = f"https://mapsv0.bdimg.com/?udt=20200825&qt=qsdata&x={lat}&y={lon}"
        return url

    def _build_metadata_url(panoID):
        """
        Build Baidu URL containing maximum zoom levels
        and older imagery.
        """
        url = f"https://mapsv0.bdimg.com/?udt=20200825&qt=sdata&sid={panoID}"
        return url

class misc:
    def get_pano_from_url(url):
        new_url = requests.get(url).url
        pano_id = re.findall('panoid=(.*)&panotype', new_url)
        return pano_id

    def short_url(pano_id):
        raise extractor.ServiceNotSupported

class metadata:
    def get_metadata(pano_id) -> str:
        url = urls._build_metadata_url(pano_id)
        data = requests.get(url).json()
        # pprint(data)
        return data

    def get_date(pano_id) -> str:
        md = metadata.get_metadata(pano_id)
        date = md['content'][0]['Date']
        return date

    def get_coords(pano_id) -> float:
        md = metadata.get_metadata(pano_id)
        lat, lng = md['content'][0]['RX'], md['content'][0]['RY']
        return lat, lng # atm returns only BD-09 coordinates

def get_pano_id(lat, lon):
    url = urls._build_pano_url(lat, lon)
    json = requests.get(url).json()
    pano_id = json["content"]["id"]
    return {
        "pano_id": pano_id
    }

def get_max_zoom(pano_id):
    """
    Finds maximum available zoom from given panorama ID.
    """
    url = urls._build_metadata_url(pano_id)
    md = requests.get(url).json()
    max = md["content"][0]["ImgLayer"][-1]["ImgLevel"] + 1
    return max

def _build_tile_arr(pano_id, zoom):
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