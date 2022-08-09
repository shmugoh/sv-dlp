import requests
from io import BytesIO
import concurrent.futures
from tqdm import tqdm

import download.tiles
import download.panorama
import services

from PIL import Image
import pillow_heif

def _download_tiles(tiles_arr):
    tiles_size = 0
    for tiles_url in tiles_arr: 
        tiles_size += len(tiles_url)

    with tqdm(total=tiles_size) as pbar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(tiles_arr)) as threads:
            for row in tiles_arr:
                tiles_arr[tiles_arr.index(row)] = threads.submit(_download_row, row, pbar)
            for thread in concurrent.futures.as_completed(tiles_arr):
                tiles_arr[tiles_arr.index(thread)] = thread.result()
    return tiles_arr

def _download_row(urls_arr, pbar) -> list:
    for url in urls_arr:
        img = requests.get(url, stream=True)
        img_io = BytesIO(img.content)
        img_io.seek(0)
        urls_arr[urls_arr.index(url)] = img_io
        pbar.update(1)
    return urls_arr

def panorama(pano, zoom, service, save_tiles=False, no_crop=False, folder='./'):
    is_coord = _is_coord(pano) # used for .csv
    if is_coord:
        print("Getting Panorama ID...")
        match service.__name__:
            case 'services.yandex':
                pano = service.get_pano_id(is_coord[0], is_coord[1])
            case _:
                pano = service.get_pano_id(is_coord[0], is_coord[1])['pano_id']

    print("Getting Metadata...")
    match service.__name__:
        case 'services.google':
            pano_name = pano
            gen = service.metadata.get_gen(pano)
        case 'services.yandex':
            pano_name = pano['oid']
            gen = None
        case 'services.apple':
            pano_name = f"{pano[0]}_{pano[1]}"
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
                if service.__name__ == 'extractor.apple':
                    img = pillow_heif.read_heif(tile)
                    img = Image.frombytes(
                        img.mode,
                        img.size,
                        img.data,
                        "raw",
                    )
                else:
                    img = Image.open(tile)
                i = f'{img_io.index(row)}_{row.index(tile)}'
                img.save(f"./{folder}/{pano}_{i}.png")

    print("Stiching Tiles...")
    with tqdm(total=len(img_io)) as pbar:
        match service.__name__:
            case 'extractor.bing':
                img = download.tiles.bing.merge(img_io, pbar)
            case 'extractor.apple':
                img = download.tiles.apple.stitch(img_io[0])
                pbar.update(1)
            case _:
                for row in img_io:
                    i = img_io.index(row)
                    img_io[i] = download.tiles.stich(row)
                    pbar.update(1)
                img = download.tiles.merge(img_io)
                pbar.update(1)
    if no_crop != True:
        print("Cropping...")
        img = download.panorama.crop(img, service.__name__, gen)

    print("Saving...")
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