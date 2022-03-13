import os
import sys
import typer
from PIL import Image

from extractor import *
from postdownload import merge_tiles
import concurrent.futures

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
    pano_id = google.get_pano_id(4.662278433183548, -74.11502894958988)["pano_id"]
    print(pano_id)
    zoom = google._find_max_zoom(pano_id)

    max_axis = google._find_max_axis(pano_id, zoom)
    tile_arr_url = google._build_tile_arr(pano_id, zoom, max_axis)
    tiles_io = merge_tiles.download_tiles(tile_arr_url)

    tile_io_array = []
    for row in tiles_io:
        buff = merge_tiles.stich_row(row)
        tile_io_array.insert(tiles_io.index(row), buff)

    final_image = merge_tiles.merge_rows(tile_io_array)
    final_image.save(f'{pano_id}.png')
