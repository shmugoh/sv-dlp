import requests
import pyproj
import math
import sv_dlp.services
from datetime import datetime

class urls:
    def _build_tile_url(bubble, tile_pos):
        """
        Build Bing StreetSide Tile URL.
        """
        url = f"https://t.ssl.ak.tiles.virtualearth.net/tiles/hs{bubble}{tile_pos}.jpg?g=11898"
        return url

    def _build_pano_url(north, south, east, west):
        """
        Build Bing URL containing Bubble ID, coordinates, and date
        from coordinate bounds.
        """
        url = f"https://t.ssl.ak.tiles.virtualearth.net/tiles/cmd/StreetSideBubbleMetaData?count=50&north={north}&south={south}&east={east}&west={west}"
        return url

    def _base4(i):
        """
        Turn Base 10 into Base 4.
        To be used with obtaining StreetSide tiles.
        """
        buff = []
        while i > 0:
                buff.insert(0, i % 4)
                i = i // 4
        buff = "".join(str(i) for i in buff)
        return buff

class geo:
    def get_bounding_box(lat, lon, radius=25):
        """
        Returns length of latitude and longitude
        within a square.

        Taken from sk-zk/streetlevel with a few changes.
        Kudos to him for saving me.
        """
        geod = pyproj.Geod(ellps="WGS84")
        dist_to_corner = math.sqrt(2 * pow(2*radius, 2)) / 2
        top_left = geod.fwd(lon, lat, 315, dist_to_corner)
        bottom_right = geod.fwd(lon, lat, 135, dist_to_corner)

        bounds = {
            "north": top_left[1],
            "south": bottom_right[1],
            "east":  bottom_right[0],
            "west": top_left[0]
        }
        return bounds

class misc:
    def get_pano_from_url(url):
        raise sv_dlp.services.ServiceNotSupported

    def short_url(pano_id):
        raise sv_dlp.services.ServiceNotSupported

class metadata:
    def get_metadata(pano_id=None, lat=None, lng=None, get_linked_panos=False) -> list:
        """
        Returns closest bubble ID and its metadata
        with parsed coordinate bounds.
        """
        if pano_id: raise sv_dlp.services.MetadataPanoIDParsed
        try:
            raw_md = metadata.get_raw_metadata(lat, lng)
            bubble_id = raw_md[1]["id"]
            base4_bubbleid = urls._base4(bubble_id)
            md = {
                "service": "bing",
                "pano_id": {"pano_id": bubble_id, "base4_panoid": str(base4_bubbleid).zfill(16)},
                "lat": raw_md[1]["lo"],
                "lng": raw_md[1]["la"],
                "date": datetime.strptime(raw_md[1]['cd'], '%m/%d/%Y %I:%M:%S %p'), # to be used with datetime
                "size": None,
                "max_zoom": 3
            }
            md['historical_panoramas'].update(None)
            if get_linked_panos == True:
                linked_panos = raw_md[2:]       # first iteration
                for panorama in linked_panos:   # is current panorama
                    md = metadata._parse_panorama(md, panorama)
            return md
        except Exception:
            raise sv_dlp.services.NoPanoIDAvailable

    def _parse_panorama(metadata, panorama_info):
        bubble_id = panorama_info["id"]
        base4_bubbleid = urls._base4(bubble_id)
        metadata["linked_panos"].update(
            {
                "pano_id": {"pano_id": bubble_id, "base4_panoid": str(base4_bubbleid).zfill(16)},
                "lat": panorama_info["lo"],
                "lng": panorama_info["la"],
                "date": datetime.strptime(panorama_info['cd'], '%m/%d/%Y %I:%M:%S %p'), # to be used with datetime
                "size": None,
                "max_zoom": 3
            }
        )
        return metadata

    def _get_raw_metadata(lat, lng) -> list:
        bounds = geo.get_bounding_box(lat, lng)
        url = urls._build_pano_url(bounds['north'], bounds['south'], bounds['east'], bounds['west'])
        json = requests.get(url).json()
        print(url)
        return json

    def get_gen(**kwargs):
        raise sv_dlp.services.ServiceNotSupported

def _build_tile_arr(metadata, zoom):
        """
        Returns available tile URLs depending on
        the level of zoom given.

        Taken from sk-zk/streetlevel with a few changes.
        Kudos to him.
        """
        base4_panoid = metadata['pano_id']['base4_panoid']
        zoom = int(zoom)
        subdivs = pow(4, zoom)
        faces = [ [] for x in range(0, 6) ]

        for tile_id in range(0, 6):
            tile_id_base4 = urls._base4(tile_id + 1).zfill(2)
            for tile in range(subdivs):
                if zoom < 1:
                    subdiv_base4 = ""
                else:
                    subdiv_base4 = urls._base4(tile).zfill(zoom)
                tile_pos = f"{tile_id_base4}{subdiv_base4}"
                url = urls._build_tile_url(base4_panoid, tile_pos)
                faces[tile_id].append(url)
        return faces
