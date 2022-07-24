from os import listdir
import requests
from io import BytesIO
import concurrent.futures
import extractor

import download.tiles
import download.panorama
from PIL import Image

def _is_coord(coords):
    try:
        coords = str(coords).split(',')
        if len(coords[-1]) == 0: coords.pop(-1)
        for coord in coords:
            if type(coord) == float:
                lat = float(coords[0][:-1])
                lng = float(coords[1])
                return lat, lng
    except ValueError:
        return False
    return False

def _download_row(urls_arr) -> list:
    for url in urls_arr:
        img = requests.get(url, stream=True)
        img_io = BytesIO(img.content)
        img_io.seek(0)

        i = urls_arr.index(url)
        urls_arr[i] = img_io
    return urls_arr
def _download_tiles(tiles_arr):
    thread_size = len(tiles_arr)
    with concurrent.futures.ThreadPoolExecutor(max_workers=thread_size) as threads:
        for row in tiles_arr:
            i = tiles_arr.index(row)
            tiles_arr[i] = threads.submit(_download_row, row)
        for thread in concurrent.futures.as_completed(tiles_arr):
            i = tiles_arr.index(thread)
            tiles_arr[i] = thread.result()
    return tiles_arr
def panorama(pano, zoom, service, save_tiles=False, no_crop=False, folder='./'):
    is_coord = _is_coord(pano) # used for .csv
    if is_coord:
        print("Getting Panorama ID...")
        match service.__name__:
            case 'extractor.yandex':
                pano = service.get_pano_id(is_coord[0], is_coord[1])
            case _:
                pano = service.get_pano_id(is_coord[0], is_coord[1])['pano_id']

    print("Getting Metadata...")
    match service.__name__:
        case 'extractor.google':
            pano_name = pano
            gen = service.metadata.get_gen(pano)
        case 'extractor.yandex':
            pano_name = pano['oid']
            gen = None
        case _:
            pano_name = pano
            gen = None
    match zoom:
        case 'max':
            zoom = service.get_max_zoom(pano)
        case -1:
            zoom = service.get_max_zoom(pano) // 2

    print("Building Tile URLs...")
    tiles_urls = service._build_tile_arr(pano, zoom)

    print("Downloading Tiles...")
    img_io = _download_tiles(tiles_urls)
    if save_tiles:
        for row in img_io:
            for tile in row:
                img = Image.open(tile)
                i = f'{img_io.index(row)}_{row.index(tile)}'
                img.save(f"./{folder}/{pano}_{i}.png")

    print("Stiching Tiles...")
    for row in img_io:
        i = img_io.index(row)
        img_io[i] = download.tiles.stich(row)
    img = download.tiles.merge(img_io)
    if no_crop != True:
        img = download.panorama.crop(img, service.__name__, gen)

    img.save(f"./{folder}/{pano_name}.png")
    return pano

def from_file(arr, zoom, service, save_tiles=False, no_crop=False, folder='./'):
    i = 0
    for pano_id in arr:
        print(f"Downloading {i}/{len(arr) - 1}")
        panorama(
            pano_id, zoom, service,
            save_tiles, no_crop, folder
        )
        i += 1