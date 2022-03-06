import requests
from PIL import Image
from io import BytesIO
import os

'''
functions below are only for reference!!
i've obtained them from my old code that
i had saved in my hard drive
'''

def download(panoID, zoom=4, keep_tiles=False): 
    # download could obtain the tile url array,
    # then make io array with the same
    # length; make threads with the length
    # of the url array, then download the x axis
    # depending on the numbered thread.
    ## while downloading, insert the image
    ## in the io array 


    # Downloads the tiles
    current_tile = 0
    max_x, current_x = 13, 0
    max_y, current_y = 5, 0
    print(max_y, max_x)
    tile_array=np.full([max_y, max_x], None)
    # print(tile_array)

    while True:
        for i in range(current_y, max_y):
            # print(current_y)
            for i in range(current_x, max_x):
                tiles.download_tile(panoID, current_x, current_y, current_tile, zoom)
                # print(current_x, current_y)
                tile_array[current_y, current_x] = (f"tile{current_tile}.png")
                # print(tile_array)
                current_tile += 1
                current_x += 1
            current_x = 0
            current_y += 1
        break
    
    # Merges the tiles
    tiles._stichTiles(tile_array)
    
    if keep_tiles is False:
        for i in range(len(tile_array)):
            for f in tile_array[i]:
                os.remove(f)
    else: pass

def _stichTiles(tile_array):
    ## make threads depending on the
    ## size of the io array, then
    ## go thru every single one of these and stich them
    ## return as an io array

    print("pain")
    print(tile_array)
    # First phase
    rows_arr = []
    for i in range(len(tile_array)):
        try:
            images = [Image.open(x) for x in tile_array[i]]
        except AttributeError: # this is gonna kill the script at some point
            continue
        widths, heights = zip(*(i.size for i in images))
        total_width, max_height = sum(widths), max(heights)  
        new_im = Image.new('RGB', (total_width, max_height))

        y = 0
        for m in images:
            print(m.filename)
            if m == images[0]:
                new_im.paste(m, (0, 0))
            else:
                new_im.paste(m, (last_image.width*y, 0))
            last_image = m
            y += 1
            new_im.save(f'tilerow{i}.png')
        rows_arr.append(f'tilerow{i}.png')

def _merge_rows(row_arr):
    # i think this would work fine
    # with the io array

    y = 0
    images = [Image.open(x) for x in row_arr]
    print(len(images))
    height = images[0].height * len(images)
    merged_im = Image.new('RGB', (images[0].width, height))

    for r in images:
        if r == images[0]:
            # m.show()
            merged_im.paste(r, (0, 0))
        else:
            merged_im.paste(r, (0, last_image.height*y))
        last_image = r
        y += 1
    merged_im.save("full_pano.png",optimize=True, quality=95)