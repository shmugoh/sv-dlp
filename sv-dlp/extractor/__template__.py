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
def _build_tile_arr(pano_id, zoom):
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


# if __name__ == "__main__":
#    pano_id = get_pano_id(39.900139527145846, 116.3958936511099)
#    zoom = _get_max_zoom(pano_id)
#    axis = _find_max_axis(pano_id, zoom)
#    tile_arr = _build_tile_arr(pano_id, zoom, axis)
#    print(tile_arr)