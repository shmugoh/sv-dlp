# Installation
To install sv-dlp, download it via PIP, as long as Python >3.10 is installed
```bash
$ pip install sv_dlp
``` 

# Getting Started
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

To download panorama directly from metadata
```python
metadata = sv_dlp.get_metadata(lat=6.603079535799973, lng=-73.99819681137278)

pano_img = sv_dlp.download_panorama(metadata['pano_id'], zoom=max)
sv_dlp.postdownload.save_panorama(pano_img, metadata)
```

## Metadata Tinkering
To obtain older and linked panoramas from given location:
```python
metadata = sv_dlp.get_metadata(lat=6.603079535799973, lng=-73.99819681137278, get_linked_panos=True)

for pano in metadata["timeline"]:
    print(pano)
for pano in metadata["linked_panos"]:
    print(pano)
```

To obtain a panorama's date:
```python
metadata = sv_dlp.get_metadata(lat=6.603079535799973, lng=-73.99819681137278)

date = metadata["date"]
print(date)
```