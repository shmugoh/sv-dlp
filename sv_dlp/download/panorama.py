from PIL import Image

def crop(img, service, gen):
    match service:
        case 'services.google':
            match img.size:
                case (512, 512): # zoom 0
                    if gen == '1' or '2/3':
                        img = img.crop((0, 0, 512, 208))
                    elif gen == '4':
                        img = img.crop((0, 0, 512, 256))

                case (1024, 512): # zoom 1
                    if gen == '1' or '2/3':
                        img = img.crop((0,0, 1024, 416))

                case (2048, 1024): # zoom 2
                    if gen == '1' or '2/3':
                        img = img.crop((0,0, 2048, 832))

                case (3584, 2048): # zoom 3
                    if gen == '1' or '2/3':
                        img = img.crop((0, 0, 3584, 1664))

                case (6656, 3584): # zoom 4
                    if gen == '2/3':
                        img = img.crop((0, 0, 6656, 3328))

        case 'services.yandex':
            match img.size:
                case (18944, 9472):
                    img = img.crop((0, 0, 18944, 6679))
    return img

if __name__ == '__main__':
    img = Image.open('FqtoFE5WkWaiAF_Ei_jMow.png')
    crop(img)