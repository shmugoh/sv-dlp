<h1 align="center">
    <b>
        sv-dlp 
    </b>
</h1>

sv-dlp is a versatile panorama scraper for a wide range of street view platforms. 
It is designed to make it easy for terminal users & developers to download panoramic images, 
acquire detailed metadata, and generate short URLs for the panoramas. The tool is built with a robust 
back-end that can handle multiple services and provides a wide range of functionalities 
such as the ability to extract metadata information, handle panorama stitching, and much more. 
Furthermore, it is designed to be easily integrable with other scripts, providing developers with 
the flexibility to incorporate its capabilities into their own projects and applications.

sv-dlp heavily relies on reverse-engineered APIs to function, as such, it is dependent on the 
stability and availability of these APIs; it's important to note that some services might change
their APIs without notice. In the event of a service not working properly, it is 
recommended to submit an issue with the Dead API label, this way, I (or a collaborator) can investigate 
and resolve the issue as soon as possible. Additionally, some services might have limitations on usage 
and it's important to respect them. In any case, I will do my best to keep sv-dlp up to date and working 
smoothly for all supported services.

This project has been made for educational purposes and all content scraped from
is owned by their respective authors.

For detailed documentation and usage examples, please refer to the [official documentation](https://juanpisss.github.io/sv-dlp/).

## **Features**
- Download Panoramas
    - A panorama ID, a coordinate or a short URL can be parsed
        - **[Google]** Radius can be parsed if input is coordinates 
    - Is multithreaded; each panorama tile row is in different threads for faster downloads
    - Saves individual tiles if `--save-tiles` is parsed
    - Download from .csv/.json files
- Fully print metadata
    - Coords, Date, Panorama ID and Gen can be printed separately
- Coordinates and short URLs are automatically turned to Panorama IDs
- Short links with a Panorama ID or coordinates

## **Services**
Service|Status|Notes
:------|:-----|:----
Google |100%  |Zoom 5 only obtains a portion of the face, but that might be Google's problem.
Baidu  |99%   |Downloading might be slow depending on how far you are from Baidu's servers; translation between BD09MC and WGS84 is innacurate.
Navae  |99%   |Short Link function does not use its appropiate API call.
Yandex |99%   |Short Link function does not use the `shortenPath` API call.
Apple  |95%   |Misc features not supported; can only obtain metadata by coords - credit to [sk-zk & retroplasma](https://github.com/juanpisss/sv-dlp/blob/master/CREDITS)
Bing   |95%   |Misc features not implemented; can only obtain metadata by coords - credit to [sk-zk](https://github.com/juanpisss/sv-dlp/blob/master/CREDITS)

## **Installation**
To install sv-dlp, download it via PIP, as long as Python >3.10 is installed
```bash
$ pip install sv_dlp
$ py -m sv_dlp
``` 
## Manual
If you prefer using a binary instead, check out the binaries [here](https://github.com/juanpisss/sv-dlp/releases/latest)
and add them to your `PATH` folder. Check out this [guide](https://www.architectryan.com/2018/03/17/add-to-the-path-on-windows-10/)
for more information.

## Getting Started
sv_dlp's features are contained within a class for syntax convenience, so to begin
import the module and declare a variable of the class
```python
import sv_dlp
sv_dlp = sv_dlp.sv_dlp()
```

### Notes
- Whenever you call any function that is relating to downloading, or translating coordinates
to Panorama ID, `self.get_metadata()` is called within that function, therefore it is 
allocated in `self.metadata`. If you plan on tinkering with the metadata,
it is is recommended to call `self_get_metadata()` first 
before calling any other function for syntax readibility.
- Metadata is returned as a `MetadataStructure` object. If you wish to use
a dictionary instead, consider using the `.dict()` method
- If you wish to call a function with a different service than google, please use
`self.set_service()` first before doing anything - input **must be lowercase**

## Downloading
To download panorama directly from coordinates:
```python
pano_img = sv_dlp.download_panorama(lat=6.603079535799973, lng=-73.99819681137278)
sv_dlp.postdownload.save_panorama(pano_img, sv_dlp.metadata)
```

To download panorama directly from Panorama ID:
```python
pano_id = sv_dlp.get_pano_id(lat=6.603079535799973, lng=-73.99819681137278)

pano_img = sv_dlp.download_panorama(pano_id)
sv_dlp.postdownload.save_panorama(pano_img, sv_dlp.metadata)
```

To download panorama directly from metadata:
```python
metadata = sv_dlp.get_metadata(lat=6.603079535799973, lng=-73.99819681137278)

pano_img = sv_dlp.download_panorama(metadata.pano_id, zoom=max)
sv_dlp.postdownload.save_panorama(pano_img, metadata)
```

To download tiles individually:
```python
pano, tiles = sv_dlp.download_panorama("YV7i9WYmvPqT5nEtFLq3SA")
sv_dlp.postdownload.save_tiles(tiles, sv_dlp.metadata)
```
You can also pass a single variable to `sv_dlp.download_panorama`,
as postdownload will automatically determine 
if it holds the panorama and tiles.

## Metadata Tinkering
To obtain older and linked panoramas from given location:
```python
metadata = sv_dlp.get_metadata(lat=6.603079535799973, lng=-73.99819681137278, get_linked_panos=True)

for pano in metadata.timeline:
    print(pano)
for pano in metadata.linked_panos:
    print(pano)
```

To obtain a panorama's date:
```python
metadata = sv_dlp.get_metadata(lat=6.603079535799973, lng=-73.99819681137278)

date = metadata.date
print(date)
```

## **FAQ**
### **Why aren't all my coordinates from .csv downloading?**
Depending on how close the given coordinates are, it'll download the same panorama ID 
no matter the difference. It's recommended to use .json or .csv with panorama IDs instead.
## **Can X Service be added?**
Depending on how accesible it is scraping-wise, yes.
**Feel free to submit in an issue** about the specific service and I'll gladly see 
what I can do about it. If you're a developer though, refer to the next question.
### **I'm a developer and I want to add X service or improve the code. Can I?**
Sure! You're welcome to submit in a pull request as long as its to improve
this program, such as improving performance, fixing a bug, adding a service, etc.
For those who want to add a service, check out [the documentation for it](https://juanpisss.github.io/sv-dlp/contributing_services/).

## **License**
[MIT](https://raw.githubusercontent.com/juanpisss/sv-dlp/master/LICENSE)
