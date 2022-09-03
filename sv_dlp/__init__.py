from . import services
from . import download
from PIL import Image

from . import version
__version__ = version.__version__

class sv_dlp:
    """
    sv_dlp classes are responsible for the API
    scrapping of various street view services.  
    Key data such as Panorama ID, service, and
    metadata are stored in sv_dlp classes for
    syntax convience    
    """
    
    def __init__(self, service="google"):
        """
        Initiates sv_dlp class by setting
        the service to scrape from, and allocating
        placeholders for pano_id and metadata
        
        Parameters
        ----------
        str:    service
            Input of service to scrape from
        
        Returns
        -------
        function:           self.service
            Function of specified service script
            
        str:                self.service_str
            String of given service's name
            
        None:               self.pano_id
            Memory Placeholder for Panorama ID
            
        None:               self.metadata
            Memory Placeholder for metadata
        """

        self.service = getattr(services, service)
        self.service_str = service
        self.pano_id = None
        self.metadata = None
        pass
    def set_service(self, service):
        """
        Picks service script from available
        attributes in ``sv_dlp.services``
        
        Parameters
        ----------
        str:    service
            Input of service to scrape from

        Returns
        -------
        function:       self.service
            Function of specified service script
            
        function:       self.service
            function of specified service script
        str:            self.service_str
            string of service's name
        """
        
        self.service = getattr(services, service)
        self.service_str = service
    def get_available_services(self, lat=None, lng=None):
        """
        Picks all compatible services
        from ``sv_dlp.services`` that works
        with specified latitude and longitude
        
        Parameters
        ----------
        float:    lat
            Latitude
        float:    lng
            Longitude

        Returns
        ----------
        list:   self.available_services
            Array of services that are
            compatible with the given input
        """
        
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

    def download_panorama(self, pano_id=None, lat=None, lng=None, zoom=3) -> Image:
        """
        Obtains Tile URLs List from a given Panorama ID/Coordinate with a
        specified zoom, downloads each row in a multithreaded way and stitches them.
        
        If self.metadata is not allocated (or does not match with given input),
        `get_metadata` is automatically called.
        
        Parameters
        ----------
        str:    pano_id
            Panorama ID - Might not work with some services
        float:  lat
            Latitude
        float:  lng
            Longitude

        Returns
        ----------
        Image:  img
            Stitched Panorama Image in PIL.Image format
        Image:  self.tile_imgs
            List of Tile Images where each element is stored
            in a PIL.Image format
        """

        if self.metadata == None or _pano_in_md(pano_id, self.metadata) is True:
            print(f"[{self.service_str}]: Obtaining Metadata...")
            if pano_id != None:
                self.get_metadata(pano_id=pano_id)
            elif lat and lng != None:
                self.get_metadata(lat=lat, lng=lng)

        if zoom == -1:
            zoom = self.metadata['max_zoom'] / 2
            zoom = round(zoom + .1)

        print(f"[{self.service_str}]: Building Tile URLs...")
        tile_arr = self.service._build_tile_arr(self.metadata, zoom)
        img, tiles_imgs = download.panorama(tile_arr, self.metadata)
        self.tiles_imgs = tiles_imgs
        return img

    def get_metadata(self, pano_id=None, lat=None, lng=None, get_linked_panos=False) -> dict:
        """
        Calls allocated service's `get_metadata()` function to obtain metadata
        with given input, and store it to class and variable.
        
        sv_dlp's metadata structure is designed with compatibility in mind, 
        allowing developers to tinker with it no matter the service picked. 
        An example of the returned metadata is the one below:
        ```python
        metadata = {
            "service": service,
            "pano_id": pano_id,
            "lat": lat,
            "lng": lng,
            "date": date, # returned as a datetime object
            "size": image_size,
            "max_zoom": len(image_avail_res[0])-1,
            "misc": { # Only use with exclusive service features
                "is_trekker": len(json[1][0][5][0][3][0][0][2]) > 3,
                "gen": gen,
            },
            "timeline": {
                [{'pano_id'}: pano_id, "date": date}],
                [{'pano_id'}: pano_id, "date": date}],
                [{'pano_id'}: pano_id, "date": date}],
                # and so on...
            }
            "linked_panos": {
                [{'pano_id'}: pano_id, "date": date, "lat": lat, "lng" lng}],
                [{'pano_id'}: pano_id, "date": date, "lat": lat, "lng" lng}],
                [{'pano_id'}: pano_id, "date": date, "lat": lat, "lng" lng}],
                # and so on... 
                # only added if get_linked_panos is true
            },
        }
        ```
        
        Parameters
        ----------
        str:    pano_id
            Panorama ID - Might not work with some services
        float:  lat
            Latitude
        float:  lng
            Longitude
        bool:   get_linked_panos
            Sets if linked panos should be returned or not

        Returns
        ----------
        dict:  metadata
            Metadata of given input
        dict:  self.metadata
            Stores metadata in class
        """
        md = self.service.metadata.get_metadata(pano_id=pano_id, lat=lat, lng=lng, get_linked_panos=get_linked_panos)
        self.metadata = md
        return md
    def get_pano_id(self, lat: float, lng: float) -> str:
        """
        Translates Latitude and Longitude to
        Panorama ID by calling class' `get_metadata()`,
        then allocates metadata and panorama ID into
        class and variable respectfully

        Parameters
        ----------
        float:  lat
            Latitude
        float:  lng
            Longitude

        Returns
        ----------
        str:    pano_id
            Panorama ID of given coordinates
        dict:   self.metadata
            Metadata of given input
        str:    self.pano_id
            Panorama ID of given coordinates
        """
        self.get_metadata(lat=lat, lng=lng)
        pano_id = self.metadata["pano_id"]
        self.pano_id = pano_id
        return pano_id

    def get_pano_from_url(self, url):
        """
        Obtains Panorama IDs from URLs.
        Shortened URLs are redirected automatically

        Parameters
        ----------
        str:  url
            (Shortened) URL containg Panorama ID

        Returns
        ----------
        str:    pano_id
            Panorama ID from given URL
        """
        pano = self.service.misc.get_pano_from_url(url)
        return pano 
    def short_url(self, pano_id=None, lat=None, lng=None):
        """
        Short URLs with parsed input using Internal API calls 
        from specified service.
        Latitude and Longitude are automatically translated to a Panorama ID,
        therefore self.pano_id is stored

        Parameters
        ----------
        str:    pano_id
            Panorama ID
        float:  lat
            Latitude
        float:  lng
            Longitude

        Returns
        ----------
        str:    url
            Shortened URL from given panorama ID
        """
        # TODO: Short Pano via Latitude/Longitude only
        if pano_id == None and self.metadata == None:
            pano_id = self.get_pano_id(lat=lng, lng=lng)
        elif self.metadata:
            pano_id = self.metadata["pano_id"]
        url = self.service.misc.short_url(pano_id)
        return url

    class postdownload:
        """
        Inner class that is responsible for tinkering
        with given panorama Image obtained from `self.download_panorama`.
        """
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

        def save_panorama(img, metadata=None, output=None):
            """
            Saves Panorama ID on local drive with
            metadata-related information (EXIF tinkering soon)
    
            Parameters
            ----------
            Image:  pano_id
                Panorama ID
            dict:   metadata
                Metadata
            str:    output
                Location (and filename) to be saved with
    
            """
            print("[pos-download]: Saving Image...")
            if output == None and metadata != None:
                pano = metadata['pano_id']
                match metadata['service']:
                    case 'yandex':
                        output = f"{pano['pano_id']}.png"
                    case 'apple':
                        output = "{pano_id}_{regional_id}.png".format(
                            pano_id=pano["pano_id"], 
                            regional_id=pano["regional_id"]
                        )
                    case "bing":
                        output = f"{pano['pano_id']}.png"
                    case _:
                        output = f"{pano}.png"
            img.save(f"./{output}", quality=95)
            # TODO: Edit EXIF data using /TNThieding/exif/ (GitLab)
    
def _pano_in_md(pano_id, md) -> bool:
    """
    Checks if Panorama ID matches
    with allocated metadata in class
    Parameters
    ----------
    str:    pano_id
        Panorama ID
    dict:   md
        Allocated Metadata in class

    Returns
    ----------
    bool:    bool
        self-explanatory 
    """
    if md["pano_id"] == pano_id:
        return True
    else:
        return False