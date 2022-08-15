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

    def download_panorama(self, pano_id=None, zoom=3, lat=None, lng=None) -> Image:
        if lat and lng:
            self.pano_id = self.get_pano_id(lat, lng)
        elif self.pano_id is None:
            self.pano_id = pano_id
        img = download.panorama(self.pano, zoom, self.service)
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