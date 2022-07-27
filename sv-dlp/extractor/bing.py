import requests
import pyproj
import math
from io import BytesIO
from PIL import Image
import extractor

class urls:
    def _build_tile_url(bubble, tile_pos):
        """
        Build Bing StreetSide Tile URL.
        """
        url = f"https://t.ssl.ak.tiles.virtualearth.net/tiles/hs{bubble}{tile_pos}.jpg?g=11898"
        return url

    def _build_pano_url(north, south, east, west):
        """
        Build Bing URL containing Bubble ID, coordinates, and date
        from coordinate bounds.
        """
        url = f"https://t.ssl.ak.tiles.virtualearth.net/tiles/cmd/StreetSideBubbleMetaData?count=1&north={north}&south={south}&east={east}&west={west}"
        return url

    def _base4(i):
        """
        Turn Base 10 into Base 4.
        To be used with obtaining StreetSide tiles.
        """
        buff = []
        while i > 0:
                buff.insert(0, i % 4)
                i = i // 4
        buff = "".join(str(i) for i in buff)
        return buff

# class misc:
    # def get_pano_from_url(url):
    #     raise extractor.ServiceNotSupported

    # def short_url(pano_id):
    #     raise extractor.ServiceNotSupported

# class metadata:
    # def get_metadata(pano_id) -> str:
    #     raise extractor.ServiceNotSupported

    # def get_date(pano_id) -> str:
    #     raise extractor.ServiceNotSupported

    # def get_coords(pano_id) -> float:
    #     raise extractor.ServiceNotSupported

    # def get_gen(pano_id):
    #     raise extractor.ServiceNotSupported

def _get_bounding_box(lat, lon, radius=25):
    """
    Returns length of latitude and longitude
    within a square.

    Taken from sk-zk/streetlevel with a few changes.
    Kudos to him for saving me.
    """
    geod = pyproj.Geod(ellps="WGS84")
    dist_to_corner = math.sqrt(2 * pow(2*radius, 2)) / 2
    top_left = geod.fwd(lon, lat, 315, dist_to_corner)
    bottom_right = geod.fwd(lon, lat, 135, dist_to_corner)

    bounds = {
        "north": top_left[1],
        "south": bottom_right[1],
        "east":  bottom_right[0],
        "west": top_left[0]
    }
    return bounds

def get_pano_id(lat, lng):
    """
    Returns closest bubble ID and its metadata
    with parsed coordinate bounds.
    """
    try:
        bounds = _get_bounding_box(lat, lng)
        url = urls._build_pano_url(bounds['north'], bounds['south'], bounds['east'], bounds['west'])
        json = requests.get(url).json()
        bubble_id = json[1]["id"]
        base4_bubbleid = urls._base4(bubble_id)

        bubble = {
            "bubble_id": bubble_id,
            "pano_id": str(base4_bubbleid).zfill(16),
            "lat": json[1]["lo"],
            "lon": json[1]["la"],
            "date": json[1]["cd"]
        }
        return bubble
    except Exception:
        raise extractor.NoPanoIDAvailable

def get_max_zoom(kwargs):
    return 3

def _build_tile_arr(base4_bubble, zoom):
        """
        Returns available tile URLs depending on
        the level of zoom given.

        Taken from sk-zk/streetlevel with a few changes.
        Kudos to him.
        """
        zoom = int(zoom)
        subdivs = pow(4, zoom)
        faces = [ [] for x in range(0, 6) ]

        for tile_id in range(0, 6):
            tile_id_base4 = urls._base4(tile_id + 1).zfill(2)
            for tile in range(subdivs):
                if zoom < 1:
                    subdiv_base4 = ""
                else:
                    subdiv_base4 = urls._base4(tile).zfill(zoom)
                tile_pos = f"{tile_id_base4}{subdiv_base4}"
                url = urls._build_tile_url(base4_bubble, tile_pos)
                faces[tile_id].append(url)
        return faces

if __name__ == '__main__':
    print(get_pano_id(-33.74429348821123, -70.73846604377563))