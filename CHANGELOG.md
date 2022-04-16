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