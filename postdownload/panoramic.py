from PIL import Image

def crop(img):
    match img.size:
        case (1024, 512):
            print(1)
            img = img.crop((0, 0, 1023, 415))
        case (3584, 2048):
            img = img.crop((0, 0, 3583, 1663))
    return img

if __name__ == '__main__':
    img = Image.open('FqtoFE5WkWaiAF_Ei_jMow.png')
    crop(img)