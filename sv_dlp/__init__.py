from . import services
from . import download
from PIL import Image

from . import version
__version__ = version.__version__

class sv_dlp:
    def __init__(self, service="google"):
        self.service = getattr(services, service)
        self.service_str = service
        self.pano_id = None
        self.metadata = None
        pass
    def set_service(self, service):
        self.service = getattr(services, service)
        self.service_str = service
    def get_available_services(self, lat=None, lng=None):
        self.available_services = []
        for service in dir(services)[::-1]:
            if service != "__spec__":
                self.set_service(service)
                try:
                    pano_id = self.get_pano_id(lat=lat, lng=lng)
                    if pano_id:
                        self.available_services.append(service)
                        self.metadata = None
                except services.NoPanoIDAvailable:
                    self.metadata = None
                    continue
            else: break
        return self.available_services

    def download_panorama(self, pano_id=None, zoom=3, lat=None, lng=None) -> Image:
        if self.metadata == None or _pano_in_md(pano_id, self.metadata) is False:
            if pano_id != None:
                self.get_metadata(pano_id=pano_id)
            elif lat and lng != None:
                self.get_metadata(lat=lat, lng=lng)
        
        tile_arr = self.service._build_tile_arr(self.metadata, zoom)
        img, tiles_imgs = download.panorama(tile_arr, self.metadata)
        self.tiles_imgs = tiles_imgs
        return img

    def get_metadata(self, pano_id=None, lat=None, lng=None, get_linked_panos=False) -> list:
        md = self.service.metadata.get_metadata(pano_id=pano_id, lat=lat, lng=lng, get_linked_panos=get_linked_panos)
        self.metadata = md
        return md
    def get_pano_id(self, lat, lng) -> str:
        self.get_metadata(lat=lat, lng=lng)
        pano_id = self.metadata["pano_id"]
        self.pano_id = pano_id
        return pano_id

    def get_pano_from_url(self, url):
        pano = self.service.misc.get_pano_from_url(url)
        return pano 
    def short_url(self, pano_id=None, lat=None, lng=None):
        # TODO: Short Pano via Latitude/Longitude only
        if pano_id == None:
            pano_id = self.get_pano_id(lat=lng, lng=lng)
        url = self.service.misc.short_url(pano_id)
        return url

    class postdownload:
        # def save_tiles(tiles_io, metadata, folder='./'):
        #     tiles_io = tiles_io[1]
        #     pano_id = metadata["pano_id"]
        #     for row in tiles_io:
        #         for tile in row:
        #             if metadata['service'] == 'apple':
        #                 img = pillow_heif.read_heif(tile)
        #                 img = Image.frombytes(img.mode, img.size, img.data, "raw")
        #             else:
        #                 img = Image.open(tile)
        #             i = f'{tiles_io.index(row)}_{row.index(tile)}'
        #             img.save(f"./{folder}/{pano_id}_{i}.png", quality=95)
        # TODO: Rework on save_tiles

        def save_panorama(img, metadata=None, output=None, folder='./'):
            if output == None and metadata != None:
                pano = metadata['pano_id']
                match metadata['service']:
                    case 'yandex':
                        output = pano['pano_id']
                    case 'apple':
                        output = "{pano_id}_{regional_id}".format(
                            pano_id=pano["pano_id"], 
                            regional_id=pano["regional_id"]
                        )
                    case "bing":
                        output = pano["pano_id"]
                    case _:
                        output = pano
            img.save(f"./{folder}/{output}.png", quality=95)
            # TODO: Edit EXIF data using /TNThieding/exif/ (GitLab)
    
def _pano_in_md(pano_id, md):
    if md["pano_id"] == pano_id:
        return True
    else:
        return False