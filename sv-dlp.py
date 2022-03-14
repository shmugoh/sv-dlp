from pprint import pprint
import sys
import typer
from extractor import *
from extractor import baidu
from postdownload import merge_tiles

app = typer.Typer()

def _is_coord(input):
    if ',' in input: return True
    else: return False

@app.command()
def metadata(
    pano: str,
    get_coords: bool=typer.Option(False, "--get-coords"),
    get_date: bool=typer.Option(False, "--get-date"),
    get_metadata: bool=typer.Option(False, "--get-metadata")):

    metadata_flags = {
        "coords": get_coords,
        "date": get_date,
        "metadata": get_metadata
    }

    is_coord = _is_coord(pano)
    if is_coord:
        pano = pano.split(',')
        lat, lon = [float(i) for i in pano]
        pano = google.get_pano_id(lat, lon)['pano_id']

    if "True" in str(metadata_flags):
        for i in metadata_flags:
            if metadata_flags[i] == True:

                match i:
                    case "coords":
                        typer.echo(google.get_coords(pano))
                    case "date":
                        typer.echo(google.get_image_date(pano))
                    case "metadata":
                        typer.echo(pprint(google.get_metadata(pano)))
                    case "trekker":
                        typer.echo(google.is_trekker(pano))

@app.command()
def download(
    pano: str,
    service: str='google',
    zoom: int=None):

    is_coord = _is_coord(pano)
    if is_coord:
        pano = pano.split(',')
        lat, lon = [float(i) for i in pano]

    match service:
        case "google":
            if lat and lon:
                pano_id = google.get_pano_id(lat, lon)['pano_id']
            if zoom == None:
                zoom = google._find_max_zoom(pano_id) // 2

            max_axis = google._find_max_axis(pano_id, zoom)
            tile_arr_url = google._build_tile_arr(pano_id, zoom, max_axis)
        case "bing":
            typer.echo("bing")
        case "baidu":
            if lat and lon:
                pano_id = baidu.get_pano_id(lat, lon)
            if zoom == None:
                zoom = baidu._get_max_zoom(pano_id)

            print(pano_id)
            max_axis = baidu._find_max_axis(pano_id, zoom)
            tile_arr_url = baidu._build_tile_arr(pano_id, zoom, max_axis)
        case _:
            typer.echo("Invalid service")
            raise typer.Exit()

    typer.echo("Downloading tiles...")
    tiles_io = merge_tiles.download_tiles(tile_arr_url)

    typer.echo("Merging tiles...")
    tile_io_array = []
    for row in tiles_io:
        buff = merge_tiles.stich_row(row)
        tile_io_array.insert(tiles_io.index(row), buff)

    final_image = merge_tiles.merge_rows(tile_io_array)
    final_image.save(f'{pano_id}.png')
    typer.echo("Done")

if __name__ == "__main__":
    app()