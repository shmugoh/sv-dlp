import sv_dlp
from pprint import pprint
sv_dlp = sv_dlp.sv_dlp()

def west_test():
    lat, lng = 37.77499382574212, -122.47185699855395 # Apple, Bing & Google
    available_services = sv_dlp.get_available_services(lat, lng)

    for service in available_services:
        _test(lat=lat, lng=lng, service=service)

def baidu_test():
    lat, lng = 39.90802391019931, 116.3403752455185
    _test(lat=lat, lng=lng, service="baidu")

def yandex_test():
    lat, lng = 55.76550473786485, 37.54340745542864
    _test(lat=lat, lng=lng, service="yandex")

def _test(lat, lng, service=""):
    print(service)
    sv_dlp.set_service(service)

    md = sv_dlp.get_metadata(lat=lat, lng=lng)
    pano = sv_dlp.get_pano_id(lat, lng)
    print(f"{md}\n\n{pano}")
    print("Downloading...")
    img = sv_dlp.download_panorama(pano_id=pano)
    print("Saving...")
    sv_dlp.postdownload.save_panorama(img, md)
    print("--------------------------------")

if __name__ == "__main__":
    print("West Services Test...")
    west_test()

    print("Baidu Service Test...")
    baidu_test()
    
    print("Yandex Test...")
    yandex_test()

    print("Short URL test...")
    pano = sv_dlp.get_pano_id(lat=6.241753550836672, lng=-75.6028728090825)
    url = sv_dlp.short_url(pano)
    print(url)
    print("--------------------------------")
    print("Get Pano ID from URl test...")
    url = sv_dlp.get_pano_from_url("https://goo.gl/maps/c1VXwkHcgj5d7sg16")
    print(url)