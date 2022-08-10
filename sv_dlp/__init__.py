from . import services
from PIL import Image
import pillow_heif

import version
__version__ = version.__version__

class sv_dlp:
    def __init__(self, service="google"):
        self.service = getattr(services, service)
        self.metadata = None
        pass
    def download_panorama(self, pano=None, zoom=3, lat=None, lng=None) -> Image:
        if lat and lng:
            self.pano = self.get_pano_id(lat, lng)
        else:
            self.pano = pano
        pass
    def get_metadata(self) -> list:
        pass
    def get_pano_id(self, lat, lng) -> str:
        pass
    def get_near_panos(self) -> str:
        pass