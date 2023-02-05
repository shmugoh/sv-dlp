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
        placeholders for pano_id and metadata.
        
        Parameters
        ----------
        str:    service
            Input of service to scrape from.
            Default is Google
        
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
        Returns all services available
        for sv_dlp. Will only return
        a specified amount if coordinates
        are parsed
        
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
                if lat != None and lng != None: # :/
                    self.set_service(service)
                    try:
                        pano_id = self.get_pano_id(lat=lat, lng=lng)
                        if pano_id:
                            self.available_services.append(service)
                            self.metadata = None
                    except services.NoPanoIDAvailable:
                        self.metadata = None
                        continue
                else: # if coords aren't parsed
                    self.available_services.append(service)
            else: break
        self.available_services.sort()
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
        Image:  tile_imgs
            List of Tile Images where each element is stored
            in a PIL.Image format
        """

        if self.metadata == None or _pano_in_md(pano_id, self.metadata) is False:
            print(f"[{self.service_str}]: Obtaining Metadata...")
            if pano_id != None:
                self.get_metadata(pano_id=pano_id)
            elif lat and lng != None:
                self.get_metadata(lat=lat, lng=lng)

        if zoom == -1:
            zoom = self.metadata.max_zoom / 2
            zoom = round(zoom + .1)

        print(f"[{self.service_str}]: Building Tile URLs...")
        tile_arr = self.service._build_tile_arr(self.metadata, zoom)
        img, tiles_imgs = download.panorama(tile_arr, self.metadata)
        return img, tiles_imgs

    def get_metadata(self, pano_id=None, lat=None, lng=None, get_linked_panos=False) -> services.MetadataStructure:
        """
        Calls allocated service's `get_metadata()` function to obtain metadata
        with given input, and store it to class and variable.
        
        Metadata is returned in a `MetadataStructure` object, providing
        the developer a more structured and organized way to handle 
        metadata information with various attributes.
        Additionally, the `.dict()` method returns the attributes of 
        each instance of the MetadataStructure class in the form of a 
        dictionary, allowing for easy access and manipulation of the 
        metadata information.
        
        sv_dlp's metadata structure is designed with compatibility in mind, 
        allowing developers to tinker with it no matter the service picked. 
        An example of the returned metadata is the one below:
        ```python
        metadata = MetadataStructure(
            service=service, 
            pano_id=pano_id, 
            lat=lat, 
            lng=lng, 
            date=datetime.datetime(), 
            size=image_size, 
            max_zoom=max_zoom, 
            timeline=[{'pano_id': 'pano_id', 'date': datetime.datetime()}], 
            linked_panos={{'pano_id': pano_id, 'lat': lat, 'lng': lng, 'date': datetime.datetime()}}, 
            misc={}
        )
        ```
        
        Additionally, the developer has the option to access the metadata 
        in dictionary form by calling the `.dict()` method. An example is:
        ```python
        metadata = {
            "service": service,
            "pano_id": pano_id,
            "lat": lat,
            "lng": lng,
            "date": datetime.datetime(),
            "size": image_size,
            "max_zoom": max_zoom,
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
        MetadataStructure:  metadata
            Metadata of given input
        MetadataStructure:  self.metadata
            Stores metadata in class
        func:               .dict()
            Function inside object that translates `MetadataStructure` object to dictionary
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
        pano_id = self.metadata.pano_id
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
    def short_url(self, pano_id=None, lat=None, lng=None, heading=0, pitch=0, zoom=90):
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
        int:    heading 
            Heading (must be around -360 - 360)
        int:    pitch
            Pitch (must be around -90 - 90)
        int:    zoom
            Zoom 

        Returns
        ----------
        str:    url
            Shortened URL from given panorama ID
        """
        # TODO: Short Pano via Latitude/Longitude only
        if pano_id == None:
            pano_id = self.get_pano_id(lat=lat, lng=lng)
        
        if -360 <= heading <= 360 or -90 <= pitch <= 90:
            url = self.service.misc.short_url(pano_id, heading=heading, pitch=pitch, zoom=zoom)
        else:
            raise services.ExceededMaxHeadingPitch
        return url

    class postdownload:
        """
        Inner class that is responsible for tinkering
        with given panorama Image obtained from `self.download_panorama`.
        """
        def save_tiles(tiles_io, metadata, output='./'):
            """
            Saves tiles individually from 
            `self.download_panorama.tile_imgs`.
            
            If 
            
            Parameters
            ----------
            Image:                  tiles_io
                List of Tile Images where each element 
                is stored in a PIL.Image format
            MetadataStructure:      metadata
                Metadata, required for Panorama ID
                & service for essential requirements
            str:                    output
                Folder to be saved onto
            """            
            if isinstance(tiles_io[1], list):
                tiles_io = tiles_io[1]
            else:
                raise services.InstanceNotTuple
            
            pano_id = metadata.pano_id
            for row in tiles_io:
                if metadata.service == 'apple':
                        import pillow_heif
                        img = pillow_heif.read_heif(row)
                        img = Image.frombytes(img.mode, img.size, img.data, "raw")
                        i = f'{tiles_io.index(row)}'
                        img.save(f"./{output}/{pano_id['pano_id']}_{pano_id['regional_id']}_{i}.png", quality=95)
                else:
                    for tile in row:
                            img = Image.open(tile)
                            i = f'{tiles_io.index(row)}_{row.index(tile)}'
                            img.save(f"./{output}/{pano_id}_{i}.png", quality=95)

        def save_panorama(img, metadata, output=None):
            """
            Saves Panorama ID on local drive with
            metadata-related information.
            
            `pano_id` must be parsed as a `PIL.Image.Image`
            object. If a list is parsed, `save_panorama` will
            treat the first element of the list as the
            panorama.
    
            Parameters
            ----------
            Image:                  img
                Panorama
            MetadataStructure:      metadata
                Metadata, required for Panorama ID
                & service for essential requirements
            str:                    output
                Location (and filename) to be saved to
    
            """
            print("[pos-download]: Saving Image...")
            
            if isinstance(img, tuple):
                if isinstance(img[0], Image.Image): 
                    img = img[0]
                else:
                    raise services.FirstInstanceNotPanorama
            
            if output == None and metadata != None:
                pano = metadata.pano_id
                match metadata.service:
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
    str:                    pano_id
        Panorama ID
    MetadataStructure:      metadata
        Allocated Metadata in class

    Returns
    ----------
    bool:    bool
        self-explanatory 
    """
    if md.pano_id == pano_id:
        return True
    else:
        return False
        
