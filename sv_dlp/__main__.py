from pprint import pprint
from sv_dlp import sv_dlp
from sv_dlp import __version__, update, services
import argparse
import string, numbers
sv_dlp = sv_dlp()
parser = argparse.ArgumentParser(
    description='''
    Download Street View panoramas from various services,
    obtain metadata and short links.
    ''',
    usage='''sv-dlp PANO ID [FLAGS]
    '''
)

_is_url = lambda url : url[0][0:4] == 'http'
def _is_coord(coords):
    strings = (string.punctuation + string.ascii_letters)
    false_positives = ['.', ',', '-']
    for c in false_positives:
        strings = strings.replace(c, '')
    try:
        for coord in coords:
            for s in strings:
                if s not in coord:
                    continue
                else: return False
            if isinstance(coord, numbers.Integral) is False:
                return True
    except ValueError:
        return False

def main(args=None):
#   --- actions ---
    parser.add_argument('-d', '--download',
        action='store_const', dest='action', const='download',
        default='download',
        help='downloads panorama to current folder')
    parser.add_argument('--download-from-file',
        action='store_const', dest='action', const='download-file',
        help='downloads each pano/coordinate from a json or csv file')
    parser.add_argument('-l', '--short-link',
        action='store_const', dest='action', const='short-link',
        help='short panorama to URL')
    parser.add_argument('--get-metadata',
        action='store_const', dest='action', const='get-metadata',
        help='obtains metadata')

    # Binary Arguments
    parser.add_argument('-u', '--update',
        action='store_const', dest='binary', const='update',
        help='update sv-dlp')
    parser.add_argument('-v', '--version',
        action='store_const', dest='binary', const='version',
        help='get current version')
#   --- metadata ---
    parser.add_argument('--get-date',
        action='store_const', dest='action', const='get-date',
        help='obtains date')
    parser.add_argument('-c', '--get-coords',
        action='store_const', dest='action', const='get-coords',
        help='obtains coords')
    parser.add_argument('-p', '--get-pano-id',
        action='store_const', dest='action', const='get-pano-id',
        help='obtains panorama id from coordinates or url')
    parser.add_argument('--get-gen',
        action='store_const', dest='action', const='get-gen',
        help='obtains gen from input. only appliable for google')
#   --- flags ---
    parser.add_argument('input',
        metavar='input', nargs="*", default=None,
        help='''
        input to scrape from. can parse panorama ID, coordinates or link. 
        parse filename instead if using --download-file
        ''')
    parser.add_argument('-s', '--service',
        metavar='', default='google',
        help='service to scrape from')
    parser.add_argument('-z', '--zoom',
        metavar='', default=(-1),
        help='sets zoom level. if not parsed, it\'ll automatically obtain half of available zoom')
    parser.add_argument('-r', '--radius',
        metavar='', default=500,
        help='sets radius level when parsing with coordinates - default is 500m')
    parser.add_argument('--linked-panos',
        action='store_true',
        help='sets if linked panos should be returned or not - only for metadata commands')
    parser.add_argument('-o', '--output',
        metavar='', default=None)
    parser.add_argument('--save-tiles',
        action='store_true',
        help='sets if tiles should be saved to current folder or not')
    parser.add_argument('--no-crop',
        action='store_true',
        help='do not crop blank bar and leave panorama as it is')
    args = parser.parse_args(args=args)
    if args.binary:
        match args.binary:
            case _:
                pass
        parser.exit(0)

    pano = args.input
    zoom = args.zoom
    service = args.service
    sv_dlp.set_service(service)

    if pano:
        if _is_url(pano):
            print("Getting Panorama ID from URL...")
            lat, lng = None, None
            pano = sv_dlp.get_pano_from_url(pano[0])
        elif _is_coord(pano):
            lat, lng = pano
            lat, lng = float(lat[:-1]), float(lng)
            pano = None
        else:
            lat, lng = None, None
            pano = pano[0]
    else: 
        parser.print_help()
        parser.exit(1)

    print(f"[{service}]: Obtaining Metadata...")
    try:
        sv_dlp.get_metadata(pano_id=pano, lat=lat, lng=lng, get_linked_panos=args.linked_panos)
        if zoom == "max":
            zoom = sv_dlp.metadata["max_zoom"]
    except services.NoPanoIDAvailable as e:
        parser.error(e.message)
    # is stored in sv_dlp.metadata

    match args.action:
        case "download":
            img = sv_dlp.download_panorama(pano_id=pano, lat=lat, lng=lng, zoom=zoom)
            sv_dlp.postdownload.save_panorama(img, sv_dlp.metadata, output=args.output)
        case "download-file":
            try:
                import json
                data = json.loads(open(pano).read())
                try:
                    pano_list = [x['panoId'] for x in data[next(iter(data))]]
                except TypeError:
                    try:
                        pano_list = [x['panoId'] for x in data['customCoordinates']]
                        if None in pano_list: pano_list.remove(None)
                    except TypeError: # if obtaind from maps-links
                        pano_list = []
                        for pano in data:
                            pano_list.append(pano)
                    # whoops
            except json.decoder.JSONDecodeError:
                del json
                csv = open(pano).read()
                pano_list = csv.split('\n')
                pano_list = [x for x in pano_list if x != '']
            
            for pano in pano_list:
                if _is_coord(pano):
                    pano = pano.split(',')
                    lat, lng = float(pano[0]), float(pano[1].strip)
                    pano = None
                img = sv_dlp.download_panorama(pano_id=pano, lat=lat, lng=lng, zoom=zoom)
                sv_dlp.postdownload.save_panorama(img, sv_dlp.metadata, output=args.output)

        case "short-link":
            try:
                print(sv_dlp.short_url(pano_id=pano, lat=lat, lng=lng))
            except services.ServiceNotSupported as error:
                parser.error(error.message)

        case "get-metadata":
            pprint(sv_dlp.metadata, sort_dicts=False)
        case "get-date":
            print(sv_dlp.metadata["date"])
        case "get-pano-id":
            print(sv_dlp.metadata["pano_id"])
        case "get-coords":
            lat = sv_dlp.metadata["lat"]
            lng = sv_dlp.metadata["lng"]
            print(lat, lng)
        case "get-gen":
            try:
                print(sv_dlp.metadata["misc"]["gen"])
            except KeyError:
                parser.error(services.ServiceNotSupported.message)

if __name__ == '__main__':
    main()