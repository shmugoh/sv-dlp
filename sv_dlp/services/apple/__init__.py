from datetime import datetime
import requests
from .auth import Authenticator
from .proto import MapTile_pb2
import math
import sv_dlp.services
# class extractor: pass

TILE_SIZE = 256

class urls:
    def _build_tile_url(pano_id, face=0, zoom=0) -> str:
            auth = Authenticator()
            url = "https://gspe72-ssl.ls.apple.com/mnn_us/"
            pano = pano_id[0]
            regional_id = pano_id[1]
            panoid_padded = pano.zfill(20)
            region_id_padded = regional_id.zfill(10)
            panoid_split = [panoid_padded[i:i + 4] for i in range(0, len(panoid_padded), 4)]
            panoid_url = "/".join(panoid_split)
            url = auth.authenticate_url(url + f"{panoid_url}/{region_id_padded}/t/{face}/{zoom}")
            return url

    def _build_metadata_url(headers) -> requests.PreparedRequest:
        prepared_request = requests.Request('GET', 'https://gspe76-ssl.ls.apple.com/api/tile?', headers).prepare()
        return prepared_request

    def _build_short_url(pano_id) -> str:
        raise sv_dlp.services.ServiceNotSupported

class misc:
    def get_pano_from_url(url):
        raise sv_dlp.services.ServiceNotSupported

    def short_url(pano_id):
        raise sv_dlp.services.ServiceNotSupported

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
    def get_metadata(pano_id=None, lat=None, lng=None, get_linked_panos=False):
        if pano_id: raise sv_dlp.services.MetadataPanoIDParsed

        session = requests.Session()
        tile_x, tile_y = geo.wgs84_to_tile_coord(lat, lng, 17)
        md_raw = metadata.get_raw_metadata(tile_x, tile_y, session)
        pano_md = md_raw.pano[0]
        lat, lng = geo.protobuf_tile_offset_to_wgs84(
                pano_md.unknown4.longitude_offset,
                pano_md.unknown4.latitude_offset,
                tile_x,
                tile_y)
        md = {
                "service": "apple",
                "pano_id": {"pano_id": pano_md.panoid, "regional_id": md_raw.unknown13[pano_md.region_id_idx].region_id},
                "lat": lat,
                "lng": lng,
                "date": datetime.fromtimestamp(int(pano_md.timestamp) / 1000.0).strftime("%Y-%m-%d %H:%M:%S"),
                "size": None,
                "max_zoom": None
            }
        md = md['historical_panoramas'].update(None)
        if get_linked_panos:
            md = metadata._parse_panorama(md, md_raw, output='linked_panos')
        return md

    def _parse_panorama(md, raw_md, output=''):
        raw_md = raw_md[1:]
        match output:
            case 'linked_panos':
                buff = {}
                for pano_info in raw_md:
                    buff.update({
                            "pano_id": {"pano_id": pano_info.panoid, "regional_id": pano_info.unknown13[pano_info.region_id_idx].region_id},
                            "lat": pano_info[2][0][-2],
                            "lng": pano_info[2][0][-1],
                            "date": datetime.fromtimestamp(int(pano_info.timestamp) / 1000.0).strftime("%Y-%m-%d %H:%M:%S"),
                    })
                md = md['linked_panos'].update(buff)

    def get_raw_metadata(tile_x, tile_y, session) -> str:
        headers = {
            "maps-tile-style": "style=57&size=2&scale=0&v=0&preflight=2",
            "maps-tile-x": str(tile_x),
            "maps-tile-y": str(tile_y),
            "maps-tile-z": "17",
            "maps-auth-token": "w31CPGRO/n7BsFPh8X7kZnFG0LDj9pAuR8nTtH3xhH8=",
        }
        response = session.send(urls._build_metadata_url(headers))
        tile = MapTile_pb2.MapTile()
        tile.ParseFromString(response.content)
        return tile

    def get_gen(pano_id):
        raise sv_dlp.services.ServiceNotSupported

def get_pano_id(lat, lon):
    try:
        md = metadata.get_metadata(lat, lon)
        pano = str(md[0]['pano'])
        regional_id = str(md[0]['regional_id'])
        resp = requests.get(urls._build_tile_url([pano, regional_id]))
        if resp.status_code != 200: raise sv_dlp.services.NoPanoIDAvailable
        return pano, regional_id
    except IndexError:
        raise sv_dlp.services.NoPanoIDAvailable

def get_max_zoom(pano_id):
    return 7

def _build_tile_arr(pano_id, zoom=0):
    max_zoom = get_max_zoom(pano_id)
    zoom = max_zoom - int(zoom)

    auth = Authenticator()
    arr = [[]]
    i = 0
    for i in range(4): # sticking to four faces at the moment
                       # cause the last two seem to not
                       # stitch well with the others
        url = urls._build_tile_url(pano_id, i, zoom)
        arr[0].append(url)
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