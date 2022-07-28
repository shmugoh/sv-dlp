## 2022.07.28
## Changelog
- **[BING]** Metadata & Misc features implemented*
    - *Short URL API hasn't been implemented
## Fixed
- **[BING]** Stiching Tiles Borked #7
## Known Bugs
- **[YANDEX]** Short URL API not working #5 
- **[GOOGLE]** Zoom 5 Stiching Tiles Borked #8
---
## 2022.07.26
## Changelog
- **[DOWNLOAD]** File not being saved correctly #14
- **[CLI]** Console will no longer print coordinates when parsing one
## Known Bugs
- **[BING]** Stiching Tiles Borked #7
- **[YANDEX]** Short URL API not working #5 
---
## 2022.07.25
## Changelog
- **[GOOGLE]** Implement Satellite Zoom and Radius - #6
- **[CLI]** Detect when input is invalid - #9
## Known Bugs
- **[BING]** Stiching Tiles Borked #7
- **[YANDEX]** Short URL API not working #5 
---
## 2022.07.24
Initial sv-dlp release (horray!!)
### Changelog
- **[GOOGLE]** Changed Metadata Selection Method
- **[GOOGLE]** Generate XDC callback
- **[GOOGLE]** Add is_trekker to metadata
- **[CLI]** Added Download Logs
- **[DOWNLOAD]** Implemented Progress Bar
### Known Bugs
- **[GOOGLE]** Coordinates to Pano ID Borked #6
- **[GOOGLE]** Zoom 5 Stiching Tiles Borked #8
- **[BING]** Stiching Tiles Borked #7
- **[YANDEX]** Short URL API not working #5 
---
## 2022.07.23
### Changelog
- **[GOOGLE]** #3 - Fix CBK API not working 
    - Replaced with GeoPhotoService.GetMetadata
    - Reverted on using the old maximum zoom technique
- **[download]** Added new Download-JSON format
---
## 2022.04.16-2
### Changelog
- Coordinates can now be parsed with quotes
- **[CLI]** Implement Update System
- **[CLI]** Add Versioning System
- **[CLI]** Update Error System
---
## 2022.04.16
Initial sv-dlp pre-release
### Changelog
- Get panorama ID from coordinate or URL (if service supports it)
- Short panorama ID or coordinate to URL (if service supports it)
- Obtain various metadata information (if service supports it)
- Download panoramas from .csv or .json (generated from [map generator](https://map-generator-flax.vercel.app/)); coordinates are automatically translated to panorama IDs.
- **[CLI]** Switched from `Typer` to `argparse`
- **[extrator]** Implemented Google, Yandex and Bing; last two doesn't have misc and metadata features yet
- **[download]** Panorama is automatically cropped depending on service and resolution
- **[download]** Implement multithreading during download of various panoramic rows
---