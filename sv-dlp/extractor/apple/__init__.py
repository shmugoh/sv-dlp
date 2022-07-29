from datetime import datetime
import requests
from .auth import Authenticator
from .proto import MapTile_pb2
import math
import extractor
# class extractor: pass

TILE_SIZE = 256

class urls:
    def _build_tile_url(pano_id, face=0, zoom=0):
            auth = Authenticator()
            url = "https://gspe72-ssl.ls.apple.com/mnn_us/"
            pano = pano_id[0]
            regional_id = pano_id[1]
            panoid_padded = str(pano).zfill(20)
            panoid_split = [panoid_padded[i:i + 4] for i in range(0, len(panoid_padded), 4)]
            panoid_url = "/".join(panoid_split)
            url = auth.authenticate_url(url + f"{panoid_url}/{regional_id}/t/{face}/{zoom}")
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

class geo:
    def protobuf_tile_offset_to_wgs84(x_offset, y_offset, tile_x, tile_y):
        """
        Calculates the absolute position of a pano from the tile offsets returned by the API.
        :param x_offset: The X coordinate of the raw tile offset returned by the API.
        :param y_offset: The Y coordinate of the raw tile offset returned by the API.
        :param tile_x: X coordinate of the tile this pano is on, at z=17.
        :param tile_y: Y coordinate of the tile this pano is on, at z=17.
        :return: The WGS84 lat/lon of the pano.
        """
        pano_x = tile_x + (x_offset / 64.0) / (TILE_SIZE - 1)
        pano_y = tile_y + (255 - (y_offset / 64.0)) / (TILE_SIZE - 1)
        lat, lon = geo.tile_coord_to_wgs84(pano_x, pano_y, 17)
        return lat, lon
    def wgs84_to_tile_coord(lat, lon, zoom):
        scale = 1 << zoom
        world_coord = geo.wgs84_to_mercator(lat, lon)
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
    def mercator_to_wgs84(x, y):
        lat = (2 * math.atan(math.exp((y - 128) / -(256 / (2 * math.pi)))) - math.pi / 2) / (math.pi / 180)
        lon = (x - 128) / (256 / 360)
        return lat, lon
    def tile_coord_to_wgs84(x, y, zoom):
        scale = 1 << zoom
        pixel_coord = (x * TILE_SIZE, y * TILE_SIZE)
        world_coord = (pixel_coord[0] / scale, pixel_coord[1] / scale)
        lat_lon = geo.mercator_to_wgs84(world_coord[0], world_coord[1])
        return lat_lon

class metadata:
    def get_metadata(lat, lng):
        tile_x, tile_y = geo.wgs84_to_tile_coord(lat, lng, 17)
        md_raw = metadata.get_raw_metadata(tile_x, tile_y)
        panos = []
        for tile in md_raw.pano:
            lat, lng = geo.protobuf_tile_offset_to_wgs84(
                tile.unknown4.longitude_offset,
                tile.unknown4.latitude_offset,
                tile_x,
                tile_y)
            panos.append(
                {
                "pano": tile.panoid,
                "regional_id": md_raw.unknown13.last_part_of_pano_url,
                "lat": lat,
                "lng": lng,
                "date": datetime.fromtimestamp(int(tile.timestamp) / 1000.0).strftime('%Y-%m-%d')
            })
        return panos

    def get_raw_metadata(tile_x, tile_y) -> str:
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

    def get_date(lat, lng) -> str:
        md = metadata.get_metadata(lat, lng)
        return md[0]['date']

    def get_coords(pano_id) -> float:
        raise extractor.ServiceNotSupported

    def get_gen(pano_id):
        raise extractor.ServiceNotSupported

def get_pano_id(lat, lon):
    try:
        md = metadata.get_metadata(lat, lon)
        pano = str(md[0]['pano'])
        regional_id = str(md[0]['regional_id'])
        resp = requests.get(urls._build_tile_url([pano, regional_id]))
        if resp.status_code != 200: raise extractor.NoPanoIDAvailable
        return pano, regional_id
    except IndexError:
        raise extractor.NoPanoIDAvailable

def get_max_zoom(pano_id):
    return 7

# last tow funcs are bit universal-ish,
# so they could work with any service
def _build_tile_arr(pano_id, zoom=0):
    max_zoom = get_max_zoom(pano_id)
    zoom = max_zoom - zoom

    auth = Authenticator()
    arr = [[]]
    i = 0
    while True:
        url = urls._build_tile_url(pano_id, i, zoom)
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