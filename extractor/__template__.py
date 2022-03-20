import requests
import extractor

class urls:
    def _build_tile_url(pano_id, x, y, zoom):
        url = f"https://example.com/?pano={pano_id}&pos={x}_{y}&zoom={zoom}"
        return url

    def _build_pano_url(lat, lon):
        url = f"https://example.com/?pano&lat={lat}&lng={lon}"
        return url

    def _build_metadata_url(pano_id):
        url = f"https://example.com/?pano={pano_id}"
        return url

    def _build_short_url(pano_id) -> str:
        raise extractor.ServiceNotSupported

class misc:
    def get_pano_from_url(url):
        raise extractor.ServiceNotSupported

    def short_url(pano_id):
        raise extractor.ServiceNotSupported

class metadata:
    def get_date(pano_id) -> str:
        raise extractor.ServiceNotSupported

    def get_metadata(pano_id) -> str:
        raise extractor.ServiceNotSupported

    def get_coords(pano_id) -> float:
        raise extractor.ServiceNotSupported

    def get_gen(pano_id):
        raise extractor.ServiceNotSupported

def get_pano_id(lat, lon):
    raise extractor.ServiceNotSupported

def get_max_zoom(pano_id):
    raise extractor.ServiceNotSupported

# last tow funcs are bit universal-ish,
# so they could work with any service
def _find_max_axis(pano_id, zoom):
    x = 0
    y = 0
    x_axis = []
    y_axis = []

    # x axis
    while True:
        url = urls._build_tile_url(pano_id, x, y, zoom)
        r = requests.get(url).status_code
        match r:
            case 200:
                x_axis = x
                x += 1
            # case 404:
            #     x += 1
            #     continue # temp
            case _:
                x = 0
                break

    # y axis
    while True:
        url = urls._build_tile_url(pano_id, x, y, zoom)
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

    for y in range(0, int(axis_arr['y']) + 1):
        for x in range(axis_arr['x']):
            url = urls._build_tile_url(pano_id, x, y, zoom)
            arr[y].append(url)
    return arr

# if __name__ == "__main__":
#    pano_id = get_pano_id(39.900139527145846, 116.3958936511099)
#    zoom = _get_max_zoom(pano_id)
#    axis = _find_max_axis(pano_id, zoom)
#    tile_arr = _build_tile_arr(pano_id, zoom, axis)
#    print(tile_arr)