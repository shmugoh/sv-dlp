import requests
import math

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

def _base4(i):
    """
    Turn Base 10 (given StreetSide MetaData ID)
    into Base 4.

    To be used with obtaining StreetSide tiles.
    """
    buff = []
    while i > 0:
            buff.insert(0, i % 4)
            i = i // 4
    buff = "".join(str(i) for i in buff)
    return buff

def get_bubble(bounds):
    """
    Returns closest bubble ID and its metadata 
    with parsed coordinate bounds.
    """

    url = f"https://t.ssl.ak.tiles.virtualearth.net/tiles/cmd/StreetSideBubbleMetaData?count=1&north={bounds['north']}&south={bounds['south']}&east={bounds['east']}&west={bounds['west']}"
    json = requests.get(url).json()

    bubble_id = json[1]["id"]
    base4_bubbleid = _base4(bubble_id)

    bubble = {                                                                                        
        "bubble_id": bubble_id,
        "base4_bubble": base4_bubbleid,
        "lat": json[1]["lo"],
        "lon": json[1]["la"],
        "date": json[1]["cd"]
    }                                                                                  
    return bubble

# https://t.ssl.ak.tiles.virtualearth.net/tiles/cmd/StreetSideBubbleMetaData?count=1&north=-33.43281436861051&south=-33.44202963138949&east=-70.63119736861051&west=-70.6404126313895
# https://www.bing.com/maps?cp=-33.437422~-70.635805&style=x&mo=z.0&v=2&sV=2&form=S00027

# -33.437422 
# -70.635805