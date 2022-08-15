from . import services
from . import download
from PIL import Image
import pillow_heif

from . import version
__version__ = version.__version__

class sv_dlp:
    def __init__(self, service="google"):
        self.service = getattr(services, service)
        self.service_str = service
        self.pano_id = None
        self.metadata = None
        pass

    def download_panorama(self, pano_id=None, zoom=3, lat=None, lng=None) -> Image:
        if pano_id != None:
            self.get_metadata(pano_id=pano_id)
        elif lat and lng != None:
            self.get_metadata(lat=lat, lng=lng)
        
        tile_arr = self.service._build_tile_arr(self.metadata, zoom)
        img, tiles_arr = download.panorama(tile_arr, self.metadata)
        self.tiles_arr = tiles_arr
        return img

    def get_metadata(self, pano_id=None, lat=None, lng=None) -> list:
        md = self.service.metadata.get_metadata(pano_id=pano_id, lat=lat, lng=lng)
        self.metadata = md
        return md
    def get_pano_id(self, lat, lng) -> str:
        if self.metadata is None:
            self.get_metadata(lat=lat, lng=lng)
        pano_id = self.metadata["pano_id"]
        self.pano_id = pano_id
        return pano_id
    # def get_linked_panos(self) -> str:
    #     sv_dlp.get_metadata(self, pano=None, lat=None, lng=None)
    #     return self.metadata['near_panos']

    class postdownload:
        def save_tiles(tiles_io, metadata, folder='./'):
            pano_id = metadata["pano_id"]
            for row in tiles_io:
                for tile in row:
                    if metadata['service'] == 'apple':
                        img = pillow_heif.read_heif(tile)
                        img = Image.frombytes(img.mode, img.size, img.data, "raw")
                    else:
                        img = Image.open(tile)
                    i = f'{tiles_io.index(row)}_{row.index(tile)}'
                    img.save(f"./{folder}/{pano_id}_{i}.png", quality=95)
        def save_panorama(img, metadata=None, output=None, folder='./'):
            if output == None and metadata != None:
                pano = metadata['pano_id']
                match metadata['service']:
                    case 'yandex':
                        pano_name = pano['oid']
                    case 'apple':
                        pano_name = f"{pano[0]}_{pano[1]}"
                    case _:
                        pano_name = pano
            img.save(f"./{folder}/{pano_name}.png", quality=95)