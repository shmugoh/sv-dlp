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
        self.metadata = None
        self.raw_metadata = None
        pass
    def download_panorama(self, pano=None, zoom=3, lat=None, lng=None) -> Image:
        if lat and lng:
            self.pano = self.get_pano_id(lat, lng)
        else:
            self.pano = pano
        img = download.panorama(self.pano, zoom, self.service)
        return img
    def get_metadata(self, pano=None, lat=None, lng=None, with_near_panos=False) -> list:
        md = self.service.metadata.get_metadata(pano=pano, lat=lat, lng=lng, with_near_panos=with_near_panos)
        self.metadata = md
        return md
    def get_pano_id(self, lat, lng) -> str:
        if self.metadata:
            return self.metadata["pano_id"]
        else:
            return self.service.get_pano_id(lat, lng)
    def get_near_panos(self) -> str:
        # TODO
        pass