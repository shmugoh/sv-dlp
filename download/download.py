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

def _download_tiles(tile_url_arr):
    tile_io_array = []
    for i in range(len(tile_url_arr)): tile_io_array.append(None)

    thread_size = len(tile_url_arr)
    with concurrent.futures.ThreadPoolExecutor(max_workers=thread_size) as threads:
        buff_arr = []
        for row in tile_url_arr:
            buff_arr.insert(tile_url_arr.index(row), threads.submit(_download_row, row))

        for thread in concurrent.futures.as_completed(buff_arr):
            tile_io_array[buff_arr.index(thread)] = thread.result()
    return tile_io_array

def panorama(pano, zoom, service, save_tiles=False, no_crop=False, folder='./', pbar=False):
    # i'm so sorry
    match service.__name__:
        case 'extractor.yandex':
            pass
        case _:
            if type(pano) == list:
                pano = pano[0]

    is_coord = _is_coord(pano) # used for .csv
    if is_coord != False:
        pano = service.get_pano_id(is_coord[0], is_coord[1])["pano_id"]

    try:
        gen = service.metadata.get_gen(pano)
    except extractor.ServiceNotSupported:
        no_crop = True
    except  extractor.ServiceFuncNotSupported:
        no_crop = True

    if zoom == 'max':
        zoom = service.get_max_zoom(pano)
    elif int(zoom) == -1:
        zoom = service.get_max_zoom(pano) // 2
    else:
        zoom = int(zoom)

    tile_arr_url = service._build_tile_arr(pano, zoom)
    tiles_io = _download_tiles(tile_arr_url)

    match service.__name__:
        case 'extractor.yandex':
            try:
                pano = pano['pano_id']
            except TypeError: # pano id already parsed
                pass

    if save_tiles:
        for row in tiles_io:
            for tile in row:
                img = Image.open(tile)
                i = f'{tiles_io.index(row)}_{row.index(tile)}'
                img.save(f"./{folder}/{pano}_{i}.png")

    tile_io_array = []
    for row in tiles_io:
        buff = download.tiles.stich(row)
        tile_io_array.insert(tiles_io.index(row), buff)
    img = download.tiles.merge(tile_io_array)
    if no_crop != True:
        img = download.panorama.crop(img, service.__name__, gen)

    img.save(f"./{folder}/{pano}.png")
    return pano

def from_file(arr, zoom, service, save_tiles=False, no_crop=False, folder='./'):
    print("Downloading...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=35) as threads:
        finished_threds = []
        threads_arr = []
        for pano in arr:
            threads_arr.append(threads.submit(panorama, pano, zoom, service, save_tiles, no_crop, folder))
        for thread in concurrent.futures.as_completed(threads_arr):
            th_num = threads_arr.index(thread)
            if th_num in finished_threds:
                pass
            else:
                finished_threds.append(th_num)

    skipped_panos = []
    for pano in arr:
        dir = listdir(folder)
        if f"{pano}.png" not in dir:
            skipped_panos.append(pano)
    print("Downloading skipped panos...")
    for pano in skipped_panos:
        download.panorama(pano, zoom, service, save_tiles, no_crop, folder)