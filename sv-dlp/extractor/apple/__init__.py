import requests
from auth import Authenticator
from proto import MapTile_pb2
import math
class extractor: pass

TILE_SIZE = 256

class urls:
    def _build_tile_url(pano_id, face, zoom):
        url = f"https://gspe72-ssl.ls.apple.com/mnn_us/0665/1337/7579/4483/3546/{pano_id}/t/{face}/{zoom}"
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

    def wgs84_to_tile_coord(lat, lon, zoom):
        scale = 1 << zoom
        world_coord = misc.wgs84_to_mercator(lat, lon)
        pixel_coord = (math.floor(world_coord[0] * scale), math.floor(world_coord[1] * scale))
        tile_coord = (math.floor((world_coord[0] * scale) / TILE_SIZE), math.floor((world_coord[1] * scale) / TILE_SIZE))
        return tile_coord
    def wgs84_to_mercator(lat, lon):
        siny = math.sin((lat * math.pi) / 180.0)
        siny = min(max(siny, -0.9999), 0.9999)
        return (
            TILE_SIZE * (0.5 + lon / 360.0),
            TILE_SIZE * (0.5 - math.log((1 + siny) / (1 - siny)) / (4 * math.pi))
        )

class metadata:
    def get_coverage_tile(tile_x, tile_y):
        headers = {
            "maps-tile-style": "style=57&size=2&scale=0&v=0&preflight=2",
            "maps-tile-x": str(tile_x),
            "maps-tile-y": str(tile_y),
            "maps-tile-z": "17",
            "maps-auth-token": "w31CPGRO/n7BsFPh8X7kZnFG0LDj9pAuR8nTtH3xhH8=",
        }
        response = requests.get("https://gspe76-ssl.ls.apple.com/api/tile?", headers=headers)
        tile = MapTile_pb2.MapTile()
        tile.ParseFromString(response.content)
        return tile

    def get_coverage_tile_by_latlon(lat, lon):
        x, y = misc.wgs84_to_tile_coord(lat, lon, 17)
        return metadata.get_coverage_tile(x, y)

    def fetch_pano_segment(panoid, that_other_id, segment, zoom, auth):
        endpoint = "https://gspe72-ssl.ls.apple.com/mnn_us/"
        panoid = str(panoid)
        if len(panoid) > 20:
            raise ValueError("panoid must not be longer than 20 characters.")
        if segment > 5:
            raise ValueError("Segments range from 0 to 5 inclusive.")

        zoom = min(7, zoom)
        panoid_padded = str(panoid).zfill(20)
        panoid_split = [panoid_padded[i:i + 4] for i in range(0, len(panoid_padded), 4)]
        panoid_url = "/".join(panoid_split)
        url = endpoint + f"{panoid_url}/{that_other_id}/t/{segment}/{zoom}"
        url = auth.authenticate_url(url)
        response = requests.get(url)
        if response.ok:
            return response.content
        else:
            raise Exception(str(response))

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
    auth = Authenticator()
    i = 0
    while True:
        url = auth.authenticate_url(urls._build_tile_url(pano_id, 0, i))
        resp = requests.get(url)
        if resp.status_code == 200:
            i += 1
        else: break
    return i

# last tow funcs are bit universal-ish,
# so they could work with any service
def _build_tile_arr(pano_id, zoom=0):
    auth = Authenticator()
    arr = [[]]
    i = 0
    while True:
        url = auth.authenticate_url(urls._build_tile_url(pano_id, i, zoom))
        resp = requests.get(url)
        if resp.status_code == 200:
            i += 1
            arr[0].append(url)
        else: break
    return arr

if __name__ == "__main__":
    print(metadata.get_coverage_tile_by_latlon(37.78076123764633, -122.47225139489618))
#    pano_id = get_pano_id(39.900139527145846, 116.3958936511099)
#    zoom = _get_max_zoom(pano_id)
#    axis = _find_max_axis(pano_id, zoom)
#    tile_arr = _build_tile_arr(pano_id, zoom, axis)
#    print(tile_arr)