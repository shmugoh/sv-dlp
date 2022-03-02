# will clean up this code later
# obtained it from my old sv code
# for now, i wanna get an idea on
# how this would work

from io import BytesIO
from PIL import Image
import requests
import re

def get_pano_id(lat, lon):
    """
    Returns closest panorama ID to given parsed coordinates.
    """

    url = f"https://maps.googleapis.com/maps/api/js/GeoPhotoService.SingleImageSearch?pb=!1m5!1sapiv3!5sUS!11m2!1m1!1b0!2m4!1m2!3d{lat}!4d{lon}!2d50!3m18!2m2!1sen!2sUS!9m1!1e2!11m12!1m3!1e2!2b1!3e2!1m3!1e3!2b1!3e2!1m3!1e10!2b1!3e2!4m6!1e1!1e2!1e3!1e4!1e8!1e6&callback=_xdc_._clm717"
    json = requests.get(url).text
    pans = re.findall(r'\[[0-9]-?,"(.+?)"].+?\[\[null,null,([0-9]+.[0-9]+),(-?[0-9]+.[0-9]+)', json) # i swear this is gonna break at some point
    pan = {                                                                                        # buuut it works for now so whatever
        "pano_id": pans[0][0],
        "lat": pans[0][1],
        "lon": pans[0][2]
    }                                                                                  
    return pan

def download_tile(panoID, x, y, i, zoom):
    """
    Downloads one Google Tile
    by given Panorama ID, position and zoom
    respectfully. 
    """
    url = "https://streetviewpixels-pa.googleapis.com/v1/tile?cb_client=maps_sv.tactile&panoid={}&x={}&y={}&zoom={}&nbt=1&fover=2"
    url = url.format(panoID, x, y, zoom)
    r = requests.get(url)
    im = Image.open(BytesIO(r.content))
    im.save(f"tile{i}.png")

# might scrape this
def _download(panoID, zoom=4, keep_tiles=False): 
    
    # Downloads the tiles
    current_tile = 0
    max_x, current_x = 13, 0
    max_y, current_y = 5, 0
    print(max_y, max_x)
    tile_array=np.full([max_y, max_x], None)
    # print(tile_array)

    while True:
        for i in range(current_y, max_y):
            # print(current_y)
            for i in range(current_x, max_x):
                tiles.download_tile(panoID, current_x, current_y, current_tile, zoom)
                # print(current_x, current_y)
                tile_array[current_y, current_x] = (f"tile{current_tile}.png")
                # print(tile_array)
                current_tile += 1
                current_x += 1
            current_x = 0
            current_y += 1
        break