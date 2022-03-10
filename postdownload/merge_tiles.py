import requests
from PIL import Image
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor
import os

'''
functions below are only for reference!!
i've obtained them from my old code that
i had saved in my hard drive
'''

def _download_row(row_arr) -> list:
    buff_arr = [] 
    for i in range(len(row_arr)): buff_arr.append(None)

    for i in range(len(buff_arr)):
        url = row_arr[i]
        img = requests.get(url, stream=True)
        buff_arr[i] = BytesIO(img.content)
    return buff_arr


def download_tiles(tile_url_arr):
    tile_io_array = [] 
    for i in range(len(tile_url_arr)): tile_io_array.append(None)

    thread_size = len(tile_url_arr)
    with ThreadPoolExecutor(max_workers=thread_size) as threads:
        thread_number = range(thread_size)
        row_arr = tile_url_arr[thread_number]

        thread = threads.submit(_download_row, row_arr)
        tile_io_array[thread_number] = thread.result()
    
    return tile_io_array

def _stich_row(row_io_arr):
    images = [Image.open(x) for x in row_io_arr]
    widths, heights = zip(*(i.size for i in images))
    total_width, max_height = sum(widths), max(heights)
    row_img = Image.new('RGB', (total_width, max_height))

    x = 0
    for m in images:
        if m == images[0]:
            row_img.paste(m, (0, 0))
        else:
            row_img.paste(m, (last_image.width*x, 0))
        last_image = m
        x += 1
    
    return row_img

def _merge_rows(rows_io_arr):
    images = [Image.open(x) for x in rows_io_arr]
    print(len(images))
    height = images[0].height * len(images)
    merged_img = Image.new('RGB', (images[0].width, height))

    y = 0
    for tile_row in images:
        if tile_row == images[0]:
            merged_img.paste(tile_row, (0, 0))
        else:
            merged_img.paste(tile_row, (0, last_image.height*y))
        last_image = tile_row
        y += 1
    
    return merged_img