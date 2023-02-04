from . import bing
from . import google
from . import yandex
from . import apple
from . import baidu
from . import navae
# i don't know why i picked this. i literally can't call extractor.[service]
# unless if i import them here, and __all__ causes pyinstaller to act very weirdly. too bad!

class MetadataStructure:
    dict_instance = []
    
    def __init__(self, service=None, pano_id=None, lat=None, lng=None, date=None, size=None, max_zoom=None, misc={}, timeline={}, linked_panos={}):
        self.service = service
        self.pano_id = pano_id
        self.lat = lat
        self.lng = lng
        self.date = date
        self.size = size
        self.max_zoom = max_zoom
        self.timeline = timeline
        self.linked_panos = linked_panos
        self.misc = misc
        self.dict_instance.append(self)
        
    def __repr__(self):
        return (
                f"{self.__class__.__name__}("
                f"service={self.service}, "
                f"pano_id={self.pano_id}, "
                f"lat={self.lat}, "
                f"lng={self.lng}, "
                f"date={self.date}, "
                f"size={self.size}, "
                f"max_zoom={self.max_zoom}, "
                f"timeline={self.timeline}, "
                f"linked_panos={self.linked_panos}, "
                f"misc={self.misc})"
        )
        
    @classmethod
    def dict(cls):
        for instance in cls.dict_instance:
            return instance.__dict__
            

class LinkedPanoStructure:
    def __init__(self, pano_id=None, lat=None, lng=None, date=None):
        self.pano_id = pano_id
        self.lat = lat
        self.lng = lng
        self.date = date

class ServiceNotSupported(Exception):
    message = "Service does not support this function"
    pass

class ServiceNotFound(Exception):
    message = "Service not found"
    pass

class ServiceShortURLFound(Exception):
    message = "Short URL used. Avoid using them as they don't work with this service"
    pass

class NoPanoIDAvailable(Exception):
    message = "Panorama ID not available in parsed coordinate"

class PanoIDInvalid(Exception):
    message = "Invalid Panorama ID. Please input a valid one and try again"

class MetadataPanoIDParsed(Exception):
    message = "Service cannot parse Panorama ID to obtain metadata"

class MetadataCoordsParsed(Exception):
    message = "Service cannot parse coordinates to obtain metadata"