# Command Line Interface User Guide

# Contents
1. [Installation](https://github.com/juanpisss/sv-dlp/wiki/Command-Line-Interface---User-Guide#installation)
2. [Getting Started - The Basics](https://github.com/juanpisss/sv-dlp/wiki/Command-Line-Interface---User-Guide#getting-started)
    1. [Downloading](https://github.com/juanpisss/sv-dlp/wiki/Command-Line-Interface---User-Guide#downloading)
    2. [Common Flags](https://github.com/juanpisss/sv-dlp/wiki/Command-Line-Interface---User-Guide#common-flags)
    3. [Metadata](https://github.com/juanpisss/sv-dlp/wiki/Command-Line-Interface---User-Guide#metadata)
3. [Available Services]()
4. [Commands / Flags](https://github.com/juanpisss/sv-dlp/wiki/Command-Line-Interface---User-Guide#commands--flags)

# Installation
To install sv-dlp, you download it via PIP (if Python >3.10 is installed) 
and using `pip sv-dlp` or by adding the binaries found in 
[the release page](https://github.com/juanpisss/sv-dlp/releases) to PATH.

# Getting Started - The Basics
sv-dlp parses arguments in various ways, the most common being:
```
sv-dlp [INPUT] [FLAGS]
```
Where `INPUT` can be a Panorama ID, Latitude and Longitude, or URL (which automatically
obtains the Panorama ID, as long as such service supports it); flags are described 
[here](https://github.com/juanpisss/sv-dlp/wiki/Command-Line-Interface---User-Guide#commands--flags), 
although the most common ones are ``--service``, where its default is google, 
and ``--zoom``, where its default is half of max zoom.
A quick example of such behaviour is:
```bash
sv-dlp 55.76550473786485, 37.54340745542864 --zoom max --service yandex
```

## Downloading
To download a single panorama with coordinates, parse them like this:
```bash
sv-dlp 37.42117099015278, -122.1016675677581
```
If a Panorama ID is available:
```bash
sv-dlp 48m9bhFEpHnA3axVSyT22w
```
And if an URL is available:
```bash
sv-dlp https://goo.gl/maps/MfDjHx8jimButM5u6
```
And so on...

You can also download tiles individually, by using:
```bash
sv-dlp "YV7i9WYmvPqT5nEtFLq3SA" --save-tiles
```

## Common Flags
If you wish to set the zoom level, leave the ``--zoom`` flag after the [INPUT], such like this:
```bash
sv-dlp 37.42117099015278, -122.1016675677581 --zoom max // can be an integer as well
```
If you wish to set another Street View service, set ``-service`` with specified service:
```bash
sv-dlp 37.77499382574212, -122.47185699855395 --service apple
```

## Metadata
sv-dlp (CLI) can fully print out metadata, one that is parsed into sv-dlp's own structure.
```bash
sv-dlp 48m9bhFEpHnA3axVSyT22w --get-metadata
```
Parsing a metadata flag will interrupt the downloading process, so please avoid this if you
wish to download a Panorama.

# Available Services
Refer to this [page]() for compatible services.

# Commands & Flags
|   Commands \| Flags  | Default |                              Usage                              |
|----------------------|---------|-----------------------------------------------------------------|
| `download`           | True    | Downloads Panorama                                              |
| `download-from-file` |         | Downloads each Panorama ID/Coordinate from a .json or .csv file |
| `--get-metadata`     |         | Prints out Metadata using sv-dlp's MD structure                 |
| `--short-link \| -l` |         | Translates Input to Shortened URL                               |
| `--service \| -s`    | google  | Sets Service to scrape from                                     |
| `--zoom \| -z`       | half    | Sets Zoom level                                                 |
| `--radius \| -r`     | 500     | Sets Radius Level when INPUT is Coordinate                      |
| `--no-crop`          | False   | Do not crop Blank Area on Panorama and leave it as it is        |
| `--save-tiles`       | False   | Saves Tiles to current folder                                   |
| `--output \| -r`     | Pano ID |                                                                 |
| `--linked-panos`     | False   | Sets if Linked Panos should appear on Metadata or not           |
| `--get-date`         |         |                                                                 |
| `--get-coords`       |         |                                                                 |
| `--get-pano-id`      |         |                                                                 |
| `--get-gen`          |         |                                                                 |
| `--heading`          |         | Sets Heading Level for shortening panorama to URL               |
| `--pitch`            |         | Sets Pitch Level for shortening panorama to URL                 |