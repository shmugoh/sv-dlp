import piexif
from PIL import Image
from fractions import Fraction

def dump_exif(metadata):
    date = metadata.date
    date_string = f"{date.year}:{date.strftime('%m')}:{date.strftime('%d')} {date.strftime('%H')}:{date.strftime('%M')}:{date.strftime('%S')}"

    lat = metadata.lat
    lng = metadata.lng
    lat_deg = _to_deg(lat, ["S", "N"])
    lng_deg = _to_deg(lng, ["W", "E"])
    exiv_lat = (_change_to_rational(lat_deg[0]), _change_to_rational(lat_deg[1]), _change_to_rational(lat_deg[2]))
    exiv_lng = (_change_to_rational(lng_deg[0]), _change_to_rational(lng_deg[1]), _change_to_rational(lng_deg[2]))

    match metadata.service:
        case "google":
            MakeModel = "Google"
            if metadata.misc["gen"] == "1":
                MakeModel = "Point Grey"
                IFDModel = "Ladybug2"
            elif metadata.misc["gen"] == "2/3":
                IFDModel = "R5 / R7"
            elif metadata.misc["gen"] == "4":
                IFDModel = "Gen 4"
        case _:
            MakeModel = str(metadata.service).capitalize()
            IFDModel = ""

    zeroth_ifd = {
                piexif.ImageIFD.DateTime: date_string,
                piexif.ImageIFD.Make: MakeModel,
                piexif.ImageIFD.Model: IFDModel
                }
    exif_ifd = {
                piexif.ExifIFD.DateTimeOriginal: date_string,
                piexif.ExifIFD.DateTimeDigitized: date_string
                }
    gps_ifd = {
        piexif.GPSIFD.GPSVersionID: (2, 0, 0, 0),
        piexif.GPSIFD.GPSLatitudeRef: lat_deg[3],
        piexif.GPSIFD.GPSLatitude: exiv_lat,
        piexif.GPSIFD.GPSLongitudeRef: lng_deg[3],
        piexif.GPSIFD.GPSLongitude: exiv_lng
    }

    exif_dict = {"0th":zeroth_ifd, "Exif":exif_ifd, "GPS":gps_ifd}
    exif_bytes = piexif.dump(exif_dict)
    return exif_bytes

def crop(img, metadata):
    match metadata.service:
        case 'google':
            match img.size:
                case (512, 512): # zoom 0
                    if metadata.misc['gen'] == '1' or '2/3':
                        img = img.crop((0, 0, 512, 208))
                    elif metadata.misc['gen']['gen'] == '4':
                        img = img.crop((0, 0, 512, 256))

                case (1024, 512): # zoom 1
                    if metadata.misc['gen'] == '1' or '2/3':
                        img = img.crop((0,0, 1024, 416))

                case (2048, 1024): # zoom 2
                    if metadata.misc['gen'] == '1' or '2/3':
                        img = img.crop((0,0, 2048, 832))

                case (3584, 2048): # zoom 3
                    if metadata.misc['gen'] == '1' or '2/3':
                        img = img.crop((0, 0, 3584, 1664))

                case (6656, 3584): # zoom 4
                    if metadata.misc['gen'] == '2/3':
                        img = img.crop((0, 0, 6656, 3328))

        case 'yandex':
            match img.size:
                case (18944, 9472):
                    img = img.crop((0, 0, 18944, 6679))
    return img

def _to_deg(value, loc):
    """
    Converts decimal coordinates into degrees, 
    munutes and seconds tuple.
    
    Taken from 
    https://gist.github.com/c060604/8a51f8999be12fc2be498e9ca56adc72.
    Thanks!

    Keyword arguments: value is float gps-value, 
    loc is direction list ["S", "N"] or ["W", "E"]
    return: tuple like (25, 13, 48.343 ,'N')
    """
    if value < 0:
        loc_value = loc[0]
    elif value > 0:
        loc_value = loc[1]
    else:
        loc_value = ""
    abs_value = abs(value)
    deg =  int(abs_value)
    t1 = (abs_value-deg)*60
    min = int(t1)
    sec = round((t1 - min)* 60, 5)
    return (deg, min, sec, loc_value)

def _change_to_rational(number):
    """
    convert a number to rantional

    Keyword arguments: number
    return: tuple like (1, 2), (numerator, denominator)
    """
    f = Fraction(str(number))
    return (f.numerator, f.denominator)

if __name__ == '__main__':
    img = Image.open('FqtoFE5WkWaiAF_Ei_jMow.png')
    crop(img)
