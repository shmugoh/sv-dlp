import requests
from io import BytesIO
import concurrent.futures
from tqdm import tqdm

from . import tiles
from . import panorama

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

def panorama(tile_urls, metadata, no_crop=False):
    print("Downloading Tiles...")
    img_io = _download_tiles(tile_urls)

    print("Stitching Tiles...")
    with tqdm(total=len(img_io)) as pbar:
        match metadata['service']:
            case 'bing':
                img = tiles.bing.merge(img_io, pbar)
            case 'apple':
                img = tiles.apple.stitch(img_io[0])
                pbar.update(1)
            case _:
                for row in img_io:
                    i = img_io.index(row)
                    img_io[i] = tiles.stitch(row)
                    pbar.update(1)
                img = tiles.merge(img_io)
                pbar.update(1)
    if no_crop != True:
        print("Cropping...")
        img = panorama.crop(img, metadata)

    return img

def from_file(arr, zoom, service, save_tiles=False, no_crop=False, folder='./'):
    i = 0
    for pano_id in arr:
        print(f"Downloading {i}/{len(arr) - 1}")
        panorama(
            pano_id, zoom, service,
            save_tiles, no_crop, folder
        )
        i += 1