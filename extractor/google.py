# will clean up this code later
# obtained it from my old sv code
# for now, i wanna get an idea on
# how this would work

from io import BytesIO
from PIL import Image
import requests
import re
import json as j

def _build_sv_url(panoID, zoom=3, x=0, y=0):
    """
    Builds Google Street View Tile URL
    """
    url = f"https://streetviewpixels-pa.googleapis.com/v1/tile?cb_client=maps_sv.tactile&panoid={panoID}&x={x}&y={y}&zoom={zoom}&nbt=1&fover=2"
    return url

def _build_photometa_url(lat, lon):
    """
    Builds Google URL. Includes panorama ID and imagery date
    """
    url = f"https://www.google.com/maps/photometa/si/v1?pb=!1m4!1smaps_sv.tactile!11m2!2m1!1b1!2m4!1m2!3d{lat}!4d{lon}!2d50!3m17!1m2!1m1!1e2!2m2!1ses-419!2sco!9m1!1e2!11m8!1m3!1e2!2b1!3e2!1m3!1e3!2b1!3e2!4m57!1e1!1e2!1e3!1e4!1e5!1e6!1e8!1e12!2m1!1e1!4m1!1i48!5m1!1e1!5m1!1e2!6m1!1e1!6m1!1e2!9m36!1m3!1e2!2b1!3e2!1m3!1e2!2b0!3e3!1m3!1e3!2b1!3e2!1m3!1e3!2b0!3e3!1m3!1e8!2b0!3e3!1m3!1e1!2b0!3e3!1m3!1e4!2b0!3e3!1m3!1e10!2b1!3e2!1m3!1e10!2b0!3e3"
    return url

def _build_geophoto_meta_url(pano_id):
    """
    Builds Google Maps API URL. Useful for metadata related stuff.
    """
    url = f'https://maps.googleapis.com/maps/api/js/GeoPhotoService.GetMetadata?pb=!1m5!1sapiv3!5sUS!11m2!1m1!1b0!2m2!1sen!2sUS!3m3!1m2!1e2!2s{pano_id}!4m6!1e1!1e2!1e3!1e4!1e8!1e6&callback=a'
    return url

def get_pano_id(lat, lon) -> list:
    """
    Returns closest Google panorama ID to given parsed coordinates.
    """

    url = _build_photometa_url(lat, lon)
    json = requests.get(url).text
    pans = re.findall(r'\[[0-9]-?,"(.+?)"].+?\[\[null,null,([0-9]+.[0-9]+),(-?[0-9]+.[0-9]+)', json)
    # formatting should be changed soon
    pan = {                                                                                        
        "pano_id": pans[0][0],
        "lat": pans[0][1],
        "lon": pans[0][2]
    }
    # when implementing -F command, it shall return various pano ids with the date
    # though keep in mind duplicates should be fixed and removed
    return pan

def _find_max_zoom(panoID):
    """
    Finds minimum and maximum available zoom from given panorama ID.
    """
    i = []
    for zoom in range(0, 6):
        url = _build_sv_url(panoID, zoom)
        r = requests.get(url).status_code
        match r:
            case 200:
                i.append(zoom)
            case _:
                pass
    return range(i[0], i[-1])

def _find_max_axis(panoID, zoom) -> dict["x", "y"]:
    x = 0
    y = 0
    x_axis = []
    y_axis = []

    # x axis
    while True:
        url = _build_sv_url(panoID, zoom, x, y)
        r = requests.get(url).status_code
        match r:
            case 200:
                x_axis = x
                x += 1
            case _:
                x = 0
                break

    # y axis
    while True:
        url = _build_sv_url(panoID, zoom, x, y)
        r = requests.get(url).status_code
        match r:
            case 200:
                y_axis = y
                y += 1
            case _:
                break
    
    max_axis = {
        "x": x_axis,
        "y": y_axis
    }
    return max_axis        

def _build_tile_arr(pano_id, zoom, axis_arr):
    arr = [] 
    for i in range(zoom):
        arr.append([])

    for y in range(0, axis_arr['y'] + 1):
        for x in range(axis_arr['x']):
            url = _build_sv_url(pano_id, zoom, x, y)
            arr[y].append(url)
    return arr

def download_tile(panoID, x, y, i, zoom):
    """
    Downloads one Google Tile
    by given Panorama ID, position and zoom
    respectfully. 
    """
    url = _build_sv_url(panoID, zoom, x, y)
    r = requests.get(url)
    im = Image.open(BytesIO(r.content))
    im.save(f"tile{i}.png")

def is_trekker(pano_id) -> bool:
    """
    Returns if given panorama ID is
    trekker or not. Might be useful
    with the planned generator.

    Thank you nur#2584 for guiding me out.
    """
    url = _build_geophoto_meta_url(pano_id)
    json = j.loads(requests.get(url).content[12:-2])
    return len(json[1][0][5][0][3][0][0][2]) > 3

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

if __name__ == "__main__":
    pano_id = "_1UQdRzymO0mdbAd8wkGMA"
    print(is_trekker(pano_id))
    # max_zoom = _find_max_zoom(pano_id)
    # half_zoom = max_zoom.stop // 2
    # print(_build_sv_url("jYxwHUdPuhm8NGfAH6y8IA", half_zoom))
    # max_axis = _find_max_axis(pano_id, half_zoom)
    # tile_arr = _build_tile_arr(pano_id, half_zoom, max_axis)
    # print(tile_arr)
    # print(len(tile_arr))