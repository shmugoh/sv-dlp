import argparse
import json
import sys

from pprint import pprint

import extractor
from extractor import * # yikes
from postdownload import download

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
            if '.' in coord and int(coord[0]): # IDK
                return True
    except ValueError:
        return False
def _is_url(url):
    if url[0][0:5] == 'https':
        return True
    else:
        return False

def main(args=None):
#   --- flags ---
    parser.add_argument('pano',
        metavar='panorama', nargs="+",
        help='input to scrape from. can be panorama ID or coordinates')
    parser.add_argument('-s', '--service',
        metavar='', nargs=1, default=['google'],
        help='service to scrape from')
    parser.add_argument('-z', '--zoom',
        metavar='', default=(-1))
    parser.add_argument('-f', '--folder',
        metavar='', default='.\\')

    parser.add_argument('--save-tiles',
        action='store_true',
        help='sets if tiles should be saved to current folder or not')
    parser.add_argument('--no-crop',
        action='store_true',
        help='do not crop blank bar and leave panorama as it is')

#   --- actions ---
    parser.add_argument('-d', '--download',
        action='store_const', dest='action', const='download',
        default='download',
        help='downloads panorama to current folder')
    parser.add_argument('--download-csv',
        action='store_const', dest='action', const='download-csv',
        help='''downloads each pano/coordinate from csv made by the generator.
        recommended to store panoramas instead, as coordinates tend
        to not download if distance is very close''')
    parser.add_argument('--download-json',
        action='store_const', dest='action', const='download-json',
        help='downloads each panorama from json made by the generator')
    parser.add_argument('-l', '--short-link',
        action='store_const', dest='action', const='short-link',
        help='only for google. short panorama to URL. coordinates are automatically converted to panorama id.')

#   --- metadata ---
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
    parser.add_argument('--get-gen',
        action='store_const', dest='action', const='get-gen',
        help='obtains gen from input')
    # parser.add_argument('--is-trekker',
    #     action='store_const', dest='action', const='is-trekker',
    #     help='obtains coords')

    args = parser.parse_args(args=args)

    try:
        service_str = args.service[0]
        service = getattr(extractor, args.service[0])
    except AttributeError:
        print("ERROR: Invalid Service")
        sys.exit(1)

    if _is_url(args.pano):
        try:
            pano = service.misc.get_pano_from_url(args.pano[0])
        except extractor.ServiceNotSupported as error:
            print(error.message)
    elif _is_coord(args.pano):
        lat = float(args.pano[0][:-1])
        lng = float(args.pano[1])

        print("Getting Panorama ID...")
        match service_str:
            case 'yandex':
                pano = service.get_pano_id(lat, lng)
            case _:
                pano = service.get_pano_id(lat, lng)["pano_id"]
    else: # panorama id
        pano = args.pano[0]

    match args.action:      # might prob divide it in divisions
        case 'download':    # such as metadata
            download.panorama(pano, args.zoom, service, args.save_tiles, args.no_crop, './', False) # yikes
        case 'download-csv':
            csv = open(pano).read()
            pano_arr = csv.split('\n')
            pano_arr = [x for x in pano_arr if x != '']

            download.from_file(pano_arr, args.zoom, service, args.save_tiles, args.no_crop, args.folder)
        case 'download-json':
            file = open(pano).read()
            data = json.loads(file)
            pano_arr = [x['panoId'] for x in data[next(iter(data))]]

            download.from_file(pano_arr, args.zoom, service, args.save_tiles, args.no_crop, args.folder)

        case 'short-link':
            try:
                print(service.misc.short_url(pano))
            except extractor.ServiceNotSupported as error:
                print(error.message)

        case 'get-metadata':
            try:
                data = service.metadata.get_metadata(pano)
                pprint(data)
            except extractor.ServiceNotSupported as error:
                print(error.message)
        case 'get-date':
            try:
                date = service.metadata.get_date(pano)
                print(date)
            except extractor.ServiceNotSupported as error:
                print(error.message)
        case 'get-pano':
            print(pano) # lol
        case 'get-coords':
            try:
                coords = service.metadata.get_coords(pano)
                print(coords)
            except extractor.ServiceNotSupported as error:
                print(error.message)
        case 'get-gen':
            try:
                gen = service.metadata.get_gen(pano)
                print(f"Gen {gen}")
            except extractor.ServiceNotSupported as error:
                print(error.message)
        # case 'is-trekker':
        #     print(service.is_trekker(pano))

if __name__ == '__main__':
    main()