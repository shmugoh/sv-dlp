import argparse
import sys
from time import sleep

import extractor
from extractor import * # yikes

from postdownload import merge_tiles

parser = argparse.ArgumentParser(
    description='''
    Download Street View panoramas from various services,
    obtain metadata and short links.
    ''',
)

'''
might move these arguments to a separate script lul
'''
parser.add_argument(
    'pano',
    metavar='pano',
    nargs="+",
    help='input to scrape from. can be panorama ID or coordinates'
)
parser.add_argument(
    '-s', '--service',
    metavar='service',
    nargs=1,
    default=['google'],
    help='service to scrape from'
)
parser.add_argument(
    '-z', '--zoom',
    metavar='zoom',
    nargs=1,
    type=int,
    default=[0],
    # help='an integer for the accumulator'
)
args = parser.parse_args()

def _is_coord(coords):
    for coord in coords:
        if float(coord[:-1]):
            return True
        else: return False

def download_panorama(tile_arr_url, keep_tiles=False):
    print("Downloading Tiles...")
    tiles_io = merge_tiles.download_tiles(tile_arr_url)

    print("Merging tiles...")
    tile_io_array = []
    for row in tiles_io:
        buff = merge_tiles.stich_row(row)
        tile_io_array.insert(tiles_io.index(row), buff)

    img = merge_tiles.merge_rows(tile_io_array)
    return img

if args.pano:
    pano = args.pano
    if _is_coord(pano):
        lat = float(pano[0][:-1])
        lng = float(pano[1])

try:
    service = getattr(extractor, args.service[0])
except AttributeError:
    print("ERROR: Invalid Service")
    sys.exit(1)

if lat and lng:
    print("Getting Panorama ID...")
    pano = service.get_pano_id(lat, lng)["pano_id"]
# print(pano)
if args.zoom == [0]:
    zoom = service.get_max_zoom(pano) // 2

print("Obtaining Tile URLs...")
max_axis = service._find_max_axis(pano, zoom)
tile_arr_url = service._build_tile_arr(pano, zoom, max_axis)


img = download_panorama(tile_arr_url)
img.save(f"{pano}.png")

# # def metadata(
# #     pano: str,
# #     get_coords: bool=typer.Option(False, "--get-coords"),
# #     get_date: bool=typer.Option(False, "--get-date"),
# #     get_metadata: bool=typer.Option(False, "--get-metadata")):

# #     metadata_flags = {
# #         "coords": get_coords,
# #         "date": get_date,
# #         "metadata": get_metadata
# #     }

# #     is_coord = _is_coord(pano)
# #     if is_coord:
# #         pano = pano.split(',')
# #         lat, lon = [float(i) for i in pano]
# #         pano = google.get_pano_id(lat, lon)['pano_id']

# #     if "True" in str(metadata_flags):
# #         for i in metadata_flags:
# #             if metadata_flags[i] == True:

# #                 match i:
# #                     case "coords":
# #                         typer.echo(google.get_coords(pano))
# #                     case "date":
# #                         typer.echo(google.get_image_date(pano))
# #                     case "metadata":
# #                         typer.echo(pprint(google.get_metadata(pano)))
# #                     case "trekker":
# #                         typer.echo(google.is_trekker(pano))
