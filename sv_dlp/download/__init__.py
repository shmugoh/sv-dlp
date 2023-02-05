import requests
from io import BytesIO
import concurrent.futures
import copy

from tqdm import tqdm

from . import tiles
from . import postdownload

def _download_tiles(tiles_arr):
    tiles_size = 0
    for tiles_url in tiles_arr: 
        tiles_size += len(tiles_url)

    with tqdm(total=tiles_size, unit="mb") as pbar:
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
    print("[download]: Downloading Tiles...")
    tiles_io = _download_tiles(tile_urls)

    print("[download]: Stitching Tiles...")
    with tqdm(total=len(tiles_io), unit="img") as pbar:
        match metadata.service:
            case 'bing':
                img = tiles.bing.merge(tiles_io, pbar)
            case 'apple':
                tiles_io = tiles_io[0]
                img = tiles.apple.stitch(tiles_io)
                pbar.update(1)
            case _:
                tiles_buff = copy.deepcopy(tiles_io)
                for row in tiles_buff:
                    i = tiles_buff.index(row)
                    tiles_buff[i] = tiles.stitch(row)
                    pbar.update(1)
                img = tiles.merge(tiles_buff)
                pbar.update(1)
    if not no_crop:
        print("[pos-download]: Cropping...")
        img = postdownload.crop(img, metadata)
    return img, tiles_io