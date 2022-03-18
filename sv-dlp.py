import argparse
import sys

from pprint import pprint

import extractor
from extractor import * # yikes
from postdownload import merge_tiles

from PIL import Image

parser = argparse.ArgumentParser(
    description='''
    Download Street View panoramas from various services,
    obtain metadata and short links.
    ''',
)

def _is_coord(coords):
    try:
        for coord in coords:
            if float(coord[:-1]):
                return True
    except ValueError:
        return False
def is_url(url):
    if url[0][0:5] == 'https':
        return True
    else:
        return False

def download_panorama(tile_arr_url, save_tiles=False):
    print("Downloading Tiles...")
    tiles_io = merge_tiles.download_tiles(tile_arr_url)

    if save_tiles:
        print("Saving Tiles...")
        for row in tiles_io:
            for tile in row:
                img = Image.open(tile)
                i = f'{tiles_io.index(row)}_{row.index(tile)}'
                img.save(f'tile{i}.png')

    print("Merging Tiles...")
    tile_io_array = []
    for row in tiles_io:
        buff = merge_tiles.stich_row(row)
        tile_io_array.insert(tiles_io.index(row), buff)

    img = merge_tiles.merge_rows(tile_io_array)
    return img

def main(args=None):
#   --- flags ---
    parser.add_argument('pano',
        metavar='panorama', nargs="+",
        help='input to scrape from. can be panorama ID or coordinates')
    parser.add_argument('-s', '--service',
        metavar='', nargs=1, default=['google'],
        help='service to scrape from')
    parser.add_argument('-z', '--zoom',
        metavar='', default=(-1),
        # help='an integer for the accumulator'
    )
    parser.add_argument('--save-tiles',
        action='store_true',
        help='sets if tiles should be saved to current folder or not')

#   --- actions ---
    parser.add_argument('-d', '--download',
        action='store_const', dest='action', const='download',
        default='download',
        help='downloads panorama to current folder')


#   --- metadata ---
    parser.add_argument('-l', '--short-link',
        action='store_const', dest='action', const='short-link',
        help='only for google. short panorama to URL. coordinates are automatically converted to panorama id.')
    parser.add_argument('--get-metadata',
        action='store_const', dest='action', const='get-metadata',
        help='obtains metadata')
    parser.add_argument('--get-date',
        action='store_const', dest='action', const='get-date',
        help='obtains date')
    parser.add_argument('--get-coords',
        action='store_const', dest='action', const='get-coords',
        help='obtains coords')
    parser.add_argument('-p', '--get-pano',
        action='store_const', dest='action', const='get-pano',
        help='obtains panorama id from coordinates or url')
    # parser.add_argument('--is-trekker',
    #     action='store_const', dest='action', const='is-trekker',
    #     help='obtains coords')

    args = parser.parse_args(args=args)

    try:
        service = getattr(extractor, args.service[0])
    except AttributeError:
        print("ERROR: Invalid Service")
        sys.exit(1)

    pano = args.pano
    if is_url(pano):
        try:
            pano = service.misc.get_pano_from_url(pano[0])[0]
        except ServiceNotSupported as error:
            print(error.message)

    if _is_coord(pano):
        lat = float(pano[0][:-1])
        lng = float(pano[1])
        pass

    try:
        if lat and lng:
            print("Getting Panorama ID...")
            pano = service.get_pano_id(lat, lng)["pano_id"]
    except NameError: # lat and lng variables not defined
        pass

    match args.action:      # might prob divide it in divisions
        case 'download':    # such as metadata
            zoom = int(args.zoom)
            if zoom == -1:
                print("Obtaining zoom...")
                zoom = service.get_max_zoom(pano) // 2
            print("Obtaining Tile URLs...")
            max_axis = service._find_max_axis(pano, zoom)
            tile_arr_url = service._build_tile_arr(pano, zoom, max_axis)

            img = download_panorama(tile_arr_url, args.save_tiles)
            img.save(f"{pano}.png")

        case 'short-link':
            try:
                print(service.misc.short_url(pano))
            except ServiceNotSupported as error:
                print(error.message)

        case 'get-metadata':
            try:
                data = service.metadata.get_metadata(pano)
                pprint(data)
            except ServiceNotSupported as error:
                print(error.message)
        case 'get-date':
            try:
                date = service.metadata.get_date(pano)
                print(date)
            except ServiceNotSupported as error:
                print(error.message)
        case 'get-pano':
            print(pano) # lol
        case 'get-coords':
            try:
                coords = service.metadata.get_coords(pano)
                print(coords)
            except ServiceNotSupported as error:
                print(error.message)
        # case 'is-trekker':
        #     print(service.is_trekker(pano))

if __name__ == '__main__':
    main()