## 2023.11.12
## Changelog
## Added
- **[GOOGLE]** Added URL-Protobuf Generation Code for improved functionality.
- **[GOOGLE]** Support for new Short URLs.
- **[BUILD | DOCS]** Added Logo
- **[DEV]** Test & Dry Build Workflow for more efficient development.
## Changed
- **[DEV]** UnitTest Workflows to ensure code reliability.
- **[DEV]** Package Versions updated for better performance and security.
- **[DEV]** Icon & Bin now included in Build Pipelines for a more comprehensive build process.
- **[DEV]** Renamed `dev_scripts` to `utils` for clearer naminng conventions
## Fixed
- **[BAIDU]** Removed Unexpected Print Statement 
## Updated
- **[DOCS]** Added Logo Images to enhance documentation visuals.
- **[DOCS]** Updated Names for consistency and clarity.
## Security
- **[BUILD]** Updated libraries to patch certain vulnerabilities
    - `certifi [2023.7.22]`: Python Charmers Future denial of service vulnerability
    - `requests [2.31.0]`: Potential Proxy-Authorization Header Leak via HTTPS
    - `certifi [2023.7.22]`: Potential Proxy-Authorization Header Leak via HTTPS
## Known Bugs 
- **[BAIDU]** Final metadata coordinates inaccurate - [#36](https://github.com/shmugoh/sv-dlp/issues/36)
- **[APPLE]** Input coordinate not accurate to output - [#25](https://github.com/shmugoh/sv-dlp/issues/25)
- **[GOOGLE]** Zoom 5 Stiching Tiles Borked [#8](https://github.com/shmugoh/sv-dlp/issues/8)

## 2023.02.06
## Changelog
## Added
- **[NAVAE]** Implemented Navae Support - #29
- **[SERVICES]** Heading, Pitching and Zooming can now be set for Short URLs
- **[DOWNLOAD]** Functionality for saving individual tiles has been reinstated
- **[DOWNLOAD]** Manipulation of EXIF data under certain circumstances is now available, including:
    - Panorama's date information
    - Panorama's coordinates
    - Panorama's camera model information
- **[DOCS]** Implement versioning for MkDocs documentation
## Changed
- **[SERVICES]** Metadata is now class-based. Use `sv_dlp.metadata.dict` for dictionary equivalent
- **[GOOGLE, BAIDU, YANDEX]** Optimized download times by 45%
- **[DOCS]** Improved grammar on documentation
## Security
- **[BUILD]** Updated various libraries to patch certain vulnerabilities
    - `future [0.18.3]`: Python Charmers Future denial of service vulnerability
    - `pillow [9.3.0]`:  Pillow subject to DoS via `SAMPLESPERPIXEL` tag
    - `protobuf [4.21.6]`: protobuf-cpp and protobuf-python have potential Denial of Service issue
    - `certifi [2022.12.07]`: Certifi removing TrustCor root certificate
---
## 2023.01.16
## Changelog
The functionality of sv-dlp's back-end can now be utilized as a constructor in other scripts, providing developers to 
easily incorporate the functionality of sv-dlp into their own projects. This makes it possible to access the various 
features and capabilities of sv-dlp, such as the ease of metadata scrapping between different services,
panorama download & stitching, etc.

## Added
- **[SERVICES]** All metadata is now returned in an unique readable format.
- **[SERVICES]** Historical Panorama & Linked Panoramas now appear in metadata.
- **[SERVICES]** Service can now be determined from input (`get_available_services`).
- **[DOWNLOAD]** TQDM Download is now properly formatted.
## Fixed
- **[BING]** Fixed Bing not downloading tiles properly
---
## 2022.07.31
## Fixed
- **[APPLE]** Fixed an issue where coordinates were not being converted to Panorama IDs correctly
- **[APPLE]** Last Panorama face is now cropped correctly
## Known Bugs 
- **[YANDEX]** Short URL API not working #5 
- **[GOOGLE]** Zoom 5 Stiching Tiles Borked #8
- **[BUILD]** pillow_heif doubling compiled executable up to 40MB #19
---
## 2022.07.30
## New Services
- **[APPLE]** Implemented Apple Look Around - #16
- **[BAIDU]** Implemented Baidu Panorama - #12
## Changelog
- **[CLI]** Datetime structure is now returned in get-date
    - **[YANDEX]** Date is now returned more precisely
- **[GOOGLE]** Short URL is now encoded
- **[CLI]** --get-coords now separates lat and lng
## Fixed
- **[CLI]** Fixed an issue where metadata commands required two arguments
## Removed
- Support for Windows x86 (32 bits) (refer to issue #19)
## Known Bugs 
- **[YANDEX]** Short URL API not working #5 
- **[GOOGLE]** Zoom 5 Stiching Tiles Borked #8
- **[BUILD]** pillow_heif doubling compiled executable up to 40MB #19
---
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
