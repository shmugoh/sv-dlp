from datetime import datetime
import requests
from .auth import Authenticator
from .proto import MapTile_pb2
from . import geo
import sv_dlp.services

class urls:
    def _build_tile_url(pano_id, face=0, zoom=0, auth=auth.Authenticator()) -> str:
            url = "https://gspe72-ssl.ls.apple.com/mnn_us/"
            pano = str(pano_id["pano_id"])
            regional_id = str(pano_id["regional_id"])
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

class metadata:
    _convert_date = lambda raw_date : datetime.fromtimestamp(int(raw_date / 1000.0))

    def get_metadata(pano_id=None, lat=None, lng=None, get_linked_panos=False):
        if pano_id: raise sv_dlp.services.MetadataPanoIDParsed
    
        session = requests.Session()
        tile_x, tile_y = geo.wgs84_to_tile_coord(lat, lng, 17)
        md_raw = metadata._get_raw_metadata(tile_x, tile_y, session)
        try:
            pano_md = md_raw.pano[0]
        except IndexError:
            raise sv_dlp.services.NoPanoIDAvailable

        lat, lng = geo.protobuf_tile_offset_to_wgs84(
                pano_md.location.longitude_offset,
                pano_md.location.latitude_offset,
                tile_x,
                tile_y)
        md = {
                "service": "apple",
                "pano_id": {
                    "pano_id": pano_md.panoid, 
                    "regional_id": md_raw.unknown13[pano_md.region_id_idx].region_id},
                "lat": lat,
                "lng": lng,
                "date": metadata._convert_date(pano_md.timestamp),
                "size": None,
                "max_zoom": 7,
                "misc": {
                    "is_trekker": md_raw.unknown13[pano_md.region_id_idx].coverage_type,
                    "north_offset": geo.get_north_offset(pano_md.location.north_x, pano_md.location.north_y),
                    "raw_elevation": pano_md.location.elevation,
                },
                "timeline": {},
            }
        md = metadata._parse_panorama(md, md_raw, output='timeline')
        if get_linked_panos:
            md = metadata._parse_panorama(md, md_raw, output='linked_panos')
        return md

    def _parse_panorama(md, raw_md, output=''):
        buff = []
        match output:
            case 'timeline':
                md['timeline'] = None
            case 'linked_panos':
                raw_md = raw_md[1:]
                for pano_info in raw_md:
                    buff.append({
                            "pano_id": {"pano_id": pano_info.panoid, "regional_id": pano_info.unknown13[pano_info.region_id_idx].region_id},
                            "lat": pano_info[2][0][-2],
                            "lng": pano_info[2][0][-1],
                            "date": datetime.fromtimestamp(int(pano_info.timestamp) / 1000.0).strftime("%Y-%m-%d %H:%M:%S"),
                    })
                md['linked_panos'] = buff
            case _:
                raise Exception
        return md

    def _get_raw_metadata(tile_x, tile_y, session) -> str:
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

    def _get_gen(pano_id):
        raise sv_dlp.services.ServiceNotSupported

def _build_tile_arr(md, zoom=0):
    pano_id = md["pano_id"]
    max_zoom = md["max_zoom"]
    zoom = max_zoom - int(zoom)

    auth = Authenticator()
    arr = [[]]
    i = 0
    for i in range(4): # sticking to four faces at the moment
                       # cause the last two seem to not
                       # stitch well with the others
        url = urls._build_tile_url(pano_id, i, zoom, auth)
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