import os
import typer
from PIL import Image

from extractor import *
from postdownload import merge_tiles
from concurrent.futures import ThreadPoolExecutor

app = typer.Typer()

def add_services(folder):
    service_arr = os.listdir(folder)
    for i in range(len(service_arr) -1):
        if service_arr[i][-3:] != '.py':
            service_arr.pop(i)
    return service_arr

@app.command()
def hello(
    name: str):

    typer.echo(f"Hello {name}")

@app.command()
def goodbye(
    name: str, 
    formal: bool = False):
    
    if formal:
        typer.echo(f"Goodbye Ms. {name}. Have a good day.")
    else:
        typer.echo(f"Bye {name}!")


if __name__ == "__main__":
    # services = add_services('extractor')
    pano_id = google.get_pano_id(-38.737475753012156, -72.59654594112037)
    print(pano_id)
    zoom = google._find_max_zoom(pano_id["pano_id"]) // 2

    max_axis = google._find_max_axis(pano_id["pano_id"], zoom)
    tile_arr_url = google._build_tile_arr(pano_id["pano_id"], zoom, max_axis)

    tiles_io = merge_tiles.download_tiles(tile_arr_url)

    tile_io_array = [] 
    for i in range(len(tiles_io)): tile_io_array.append(None)

    thread_size = len(tiles_io)
    with ThreadPoolExecutor(max_workers=thread_size) as threads:
        thread_count = int(threads._thread_name_prefix[-1])
        row_arr = tile_io_array[thread_count]

        thread = threads.submit(merge_tiles.stich_row, row_arr)
        tile_io_array[thread_count] = thread.result()
    
    final_image = merge_tiles.merge_rows(tile_io_array)
    final_image.save("pano.png")
