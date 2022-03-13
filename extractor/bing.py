from multiprocessing.sharedctypes import Value
import requests
import webbrowser
import math
from io import BytesIO
from PIL import Image

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

def _get_bounding_box(lat, lon):
    '''
    Obtain bounding box of coordinates to
    parse coordinate to Bing's API.

    For more info, see https://en.wikipedia.org/wiki/Latitude#Length_of_a_degree_of_latitude

    Also see https://stackoverflow.com/questions/62719999/how-can-i-convert-latitude-longitude-into-north-south-east-west-if-its-possib
    '''
    pi = math.pi
    eSq = 0.00669437999014 # eccentricity squared
    a = 6378137.0 # equatorial radius
    lat = lat * pi / 180
    lon = lon * pi / 180

    lat_len = (pi * a * (1 - eSq)) / (180 * math.pow((1 - eSq * math.pow(math.sin(lat), 2)), 3 / 2))
    lon_len = (pi * a * math.cos(lon)) / (180 * math.sqrt((1 - (eSq * math.pow(math.sin(lon), 2)))))

    bounds = {
        "north": lat + (1000 / lat_len),
        "south": lat - (1000 / lat_len),
        "east": lon + (1000 / lon_len),
        "west": lon - (1000 / lon_len)
    }
    return bounds

def _find_axis(base4_bubble, zoom=2):
    """
    Returns available tiles depending on
    the level of zoom given.

    Returns multiple arguments to be given next to
    encoded Bubble while building the url

    Taken from sk-zk/streetlevel with a few changes.
    Kudos to him.
    """
    if zoom > 3:
        raise ValueError("Zoom can't be greater than 3")

    arr = []
    for i in range(0, 6):
        arr.append([])
    print(arr)

    max_tiles = int(math.pow(4, zoom))
    for tile_id in range(0, 6):
        tile_id_base4 = urls._base4(tile_id + 1).zfill(2)
        for group in range(0, max_tiles):
            if zoom < 1:
                subdiv_base4 = ""
            else:
                subdiv_base4 = urls._base4(group).zfill(zoom)
            tile_pos = f"{tile_id_base4}{subdiv_base4}"
            print(f"hs{base4_bubble}{tile_pos}", tile_id_base4, group)
            arr[tile_id].append(tile_pos)

    return arr


def get_bubble(bounds):
    """
    Returns closest bubble ID and its metadata
    with parsed coordinate bounds.
    """

    url = urls._build_tile_url(bounds['north'], bounds['south'], bounds['east'], bounds['west'])
    json = requests.get(url).json()

    bubble_id = json[1]["id"]
    base4_bubbleid = urls._base4(bubble_id)

    bubble = {
        "bubble_id": bubble_id,
        "base4_bubble": str(base4_bubbleid).zfill(16),
        "lat": json[1]["lo"],
        "lon": json[1]["la"],
        "date": json[1]["cd"]
    }
    return bubble

# def download_tile(bubble, title_pos):
#     url = urls._build_tile_url(bubble, title_pos)
#     r = requests.get(url)
#     im = Image.open(BytesIO(r.content))
#     im.save(f"tile{i}.png")

# https://t.ssl.ak.tiles.virtualearth.net/tiles/cmd/StreetSideBubbleMetaData?count=1&north=-33.43281436861051&south=-33.44202963138949&east=-70.63119736861051&west=-70.6404126313895
# https://www.bing.com/maps?cp=-33.437422~-70.635805&style=x&mo=z.0&v=2&sV=2&form=S00027

# -33.437422
# -70.635805

if __name__ == '__main__':
    _find_axis(urls._base4(118031601).zfill(16))