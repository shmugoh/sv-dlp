from . import services
from . import download
from PIL import Image

from . import version
__version__ = version.__version__

class sv_dlp:
    def __init__(self, service="google"):
        self.service = getattr(services, service)
        self.service_str = service
        self.pano = None
        self.metadata = None
        pass
    def download_panorama(self, pano=None, zoom=3, lat=None, lng=None) -> Image:
        if lat and lng:
            self.pano = self.get_pano_id(lat, lng)
        elif self.pano is None:
            self.pano = pano
        img = download.panorama(self.pano, zoom, self.service)
        return img
    def get_metadata(self, pano=None, lat=None, lng=None, with_near_panos=False) -> list:
        md = self.service.metadata.get_metadata(pano=pano, lat=lat, lng=lng, with_near_panos=with_near_panos)
        self.metadata = md
        return md
    def get_pano_id(self, lat, lng) -> str:
        if self.metadata:
            pano = self.metadata["pano_id"]
        else:
            pano = self.service.get_pano_id(lat, lng)
        self.pano = pano
        return pano
    def get_near_panos(self) -> str:
        sv_dlp.get_metadata(self, pano=None, lat=None, lng=None, with_near_panos=True)
        return self.metadata['near_panos']