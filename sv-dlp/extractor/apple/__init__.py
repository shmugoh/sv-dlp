import requests
from .auth import Authenticator
from .proto import MapTile_pb2
import math
import extractor
# class extractor: pass

TILE_SIZE = 256

class urls:
    def _build_tile_url(pano_id, face=0, zoom=0):
            url = "https://gspe72-ssl.ls.apple.com/mnn_us/"
            pano = pano_id[0]
            regional_id = pano_id[1]
            zoom = min(7, zoom)
            panoid_padded = str(pano).zfill(20)
            panoid_split = [panoid_padded[i:i + 4] for i in range(0, len(panoid_padded), 4)]
            panoid_url = "/".join(panoid_split)
            url = url + f"{panoid_url}/{regional_id}/t/{face}/{zoom}"
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
    def get_metadata(lat, lon) -> str:
        tile_x, tile_y = misc.wgs84_to_tile_coord(lat, lon, 17)
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

    def get_date(pano_id) -> str:
        raise extractor.ServiceNotSupported

    def get_coords(pano_id) -> float:
        raise extractor.ServiceNotSupported

    def get_gen(pano_id):
        raise extractor.ServiceNotSupported

def get_pano_id(lat, lon):
    try:
        md = metadata.get_metadata(lat, lon)
        with open('hi', 'w+') as f:
            f.write(str(md))
        pano = str(md.pano[0].panoid)
        regional_id = str(md.unknown13.last_part_of_pano_url)
        return pano, regional_id
    except IndexError:
        raise extractor.NoPanoIDAvailable

def get_max_zoom(pano_id):
    return 6

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

# if __name__ == "__main__":
#     auth = Authenticator()
#     pans = get_pano_id(50.655802929382766, 9.678869633691273)
#     print(urls._build_tile_url(pans))

#    pano_id = get_pano_id(39.900139527145846, 116.3958936511099)
#    zoom = _get_max_zoom(pano_id)
#    axis = _find_max_axis(pano_id, zoom)
#    tile_arr = _build_tile_arr(pano_id, zoom, axis)
#    print(tile_arr)