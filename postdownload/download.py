import requests
from io import BytesIO
import concurrent.futures

import postdownload.tiles as tiles
import postdownload.panoramic as panoramic
from PIL import Image

from tqdm import tqdm

def _is_coord(coords):
    try:
        coords = str(coords).split(',')
        if coords[-1] == '': coords.pop(-1)
        for coord in coords:
            if float(coord):
                lat = float(coords[0][:-1])
                lng = float(coords[1])
                return lat, lng
    except ValueError:
        return False

def _download_row(row_arr) -> list:
    buff_arr = []
    for i in range(len(row_arr)): buff_arr.append(None)

    for i in range(len(buff_arr)):
        url = row_arr[i]
        img = requests.get(url, stream=True)
        img_io = BytesIO(img.content)
        # print(img.status_code)
        # print(img.url)
        img_io.seek(0)
        buff_arr[i] = img_io
    return buff_arr

def _download_tiles(tile_url_arr):
    tile_io_array = []
    for i in range(len(tile_url_arr)): tile_io_array.append(None)

    # for i in range(len(tile_url_arr)):
    #     thread = threading.Thread(target=_download_row, args=(tile_url_arr[i],))
    #     threads.append(thread)
    #     thread.start()
    #     tile_io_array[i] = thread.join()

    thread_size = len(tile_url_arr)
    with concurrent.futures.ThreadPoolExecutor(max_workers=thread_size) as threads:
        buff_arr = []
        for row in tile_url_arr:
            buff_arr.insert(tile_url_arr.index(row), threads.submit(_download_row, row))

        for thread in concurrent.futures.as_completed(buff_arr):
            tile_io_array[buff_arr.index(thread)] = thread.result()

        # tile_io_array[thread_number] = thread.result()
    return tile_io_array

def panorama(pano, zoom, service, save_tiles=False, folder=None, pbar=False):
    is_coord = _is_coord(pano)
    if is_coord != False:
        pano = service.get_pano_id(is_coord[0], is_coord[1])["pano_id"]

    if pbar:
        pbar = tqdm(total=3)

    if zoom == 'max':
        zoom = service.get_max_zoom(pano)
    elif int(zoom) == -1:
        zoom = service.get_max_zoom(pano) // 2
    if pbar: pbar.update(1)

    tile_arr_url = service._build_tile_arr(pano, zoom)
    if pbar: pbar.update(1)
    tiles_io = _download_tiles(tile_arr_url)
    if pbar: pbar.update(1)

    if save_tiles:
        for row in tiles_io:
            for tile in row:
                img = Image.open(tile)
                i = f'{tiles_io.index(row)}_{row.index(tile)}'
                img.save(f"./{folder}/{pano}_{i}.png")

    tile_io_array = []
    for row in tiles_io:
        buff = tiles.stich(row)
        tile_io_array.insert(tiles_io.index(row), buff)
    if pbar: pbar.update(1)
    img = tiles.merge(tile_io_array)
    if pbar: pbar.update(1)

    panoramic.crop(img)
    if pbar: pbar.update(1)

    if folder != None: # auto-save with a horrible name
        img.save(f"./{folder}/{pano}.png")
    else:
        return img

def from_file(arr, zoom, service, save_tiles, folder):
    print("Downloading...")
    pbar = tqdm(total=(len(arr)), leave=False)
    with concurrent.futures.ThreadPoolExecutor(max_workers=35) as threads:
        finished_threds = []
        threads_arr = []
        for pano in arr:
            threads_arr.append(threads.submit(panorama, pano, zoom, service, save_tiles, folder))
        for thread in concurrent.futures.as_completed(threads_arr):
            th_num = threads_arr.index(thread)
            if th_num in finished_threds:
                pass
            else:
                finished_threds.append(th_num)
                pbar.update(1)