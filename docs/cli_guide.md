# Command Line Interface User Guide for sv-dlp

## Table of Contents
1. [Installation Guidelines](#installation-guidelines)
2. [Introduction to Basics](#introduction-to-basics)
    1. [Procedure for Downloading](#procedure-for-downloading)
    2. [Overview of Common Flags](#overview-of-common-flags)
    3. [Accessing Metadata](#accessing-metadata)
3. [List of Supported Services](#list-of-supported-services)
4. [Detailed Command and Flag Descriptions](#detailed-command-and-flag-descriptions)

## Installation Guidelines
To begin the installation of sv-dlp, users with Python version 3.10 or higher should utilize PIP. 
Execute the command `pip install sv-dlp` for a standard installation. 

Alternatively, binaries are available on [the release page](https://github.com/shmugoh/sv-dlp/releases). 
Ensure these binaries are properly added to your system's PATH for optimal functionality.

## Introduction to Basics
sv-dlp processes arguments in multiple forms. A typical command structure is illustrated below:
```bash
sv-dlp [INPUT] [FLAGS]
```
The `INPUT` parameter accepts formats such as Panorama ID, Latitude and Longitude coordinates, or a direct URL. 
- The URL input automatically retrieves the Panorama ID if supported by the service. 
- Flags modify the behavior of sv-dlp (CLI) and are elaborated in detail [here](#common-flags).     
    - Notable flags include `--service`, defaulting to Google, and `--zoom`, with a default setting at half of the maximum zoom level. For instance:
        ```bash
        sv-dlp 55.76550473786485, 37.54340745542864 --zoom max --service yandex
        ```

## Procedure for Downloading
To download a single panorama using coordinates, use the following command:
```bash
sv-dlp 37.42117099015278, -122.1016675677581
```
For downloading using a Panorama ID:
```bash
sv-dlp 48m9bhFEpHnA3axVSyT22w
```
For URLs:
```bash
sv-dlp https://goo.gl/maps/MfDjHx8jimButM5u6
```
To download individual tiles:
```bash
$ sv-dlp "YV7i9WYmvPqT5nEtFLq3SA" --save-tiles
```

## Overview of Common Flags
To specify the zoom level, append the `--zoom` flag after the input. This flag accepts both integer values and certain keywords (max being the only one supported):
```bash
sv-dlp 37.42117099015278, -122.1016675677581 --zoom max
```
To utilize a different Street View service, the `--service` flag should be set as follows:
```bash
sv-dlp 37.77499382574212, -122.47185699855395 --service apple
```

## Accessing Metadata
sv-dlp is capable of outputting comprehensive metadata in a 
structured format specific to sv-dlp. To retrieve metadata:
```bash
sv-dlp 48m9bhFEpHnA3axVSyT22w --get-metadata
```
Note: Activating the metadata flag halts the panorama downloading process. 
Use this function at your own discretion when looking to extract panoramic images.

# List of Supported Services
{%
   include-markdown "../README.md"
   start="## **Services**"
   end="## **Installation**"
%}

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