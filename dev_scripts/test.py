"""
Shall be ran under parent directory
with python -m dev_scripts.test
"""
import sys
import sv_dlp
from pprint import pprint
sv_dlp = sv_dlp.sv_dlp()

def _pano_test(pano_id, service):
    print(f"\n{service} panorama test")
    sv_dlp.set_service(service)

    md = sv_dlp.get_metadata(pano_id)
    print(f"{md}\n{pano_id}")
    print("Downloading...")
    img = sv_dlp.download_panorama(pano_id=pano_id)
    print("Saving...")
    sv_dlp.postdownload.save_panorama(img, md)

def _ll_test(lat, lng, service):
    print(f"\n{service} download/metadata coordinate test")
    sv_dlp.set_service(service)

    md = sv_dlp.get_metadata(lat=lat, lng=lng)
    pano = sv_dlp.get_pano_id(lat, lng)
    print(f"{md}\n{pano}")
    print("Downloading...")
    img = sv_dlp.download_panorama(pano_id=pano)
    print("Saving...")
    sv_dlp.postdownload.save_panorama(img, md)

if __name__ == "__main__":
    available_services = sv_dlp.get_available_services()
    print("Download/Metadata Test")
    west_services = ["apple", "bing", "google"]

    for service in available_services:
        if service in west_services:
            lat, lng = 37.77499382574212, -122.47185699855395
            _ll_test(lat=lat, lng=lng, service=service)
            if service == "google":
                _pano_test(pano_id="YV7i9WYmvPqT5nEtFLq3SA", service=service)
        elif service == "baidu":
            lat, lng = 39.90802391019931, 116.3403752455185
            pano_id = "09026600011611300908478628V"
            _ll_test(lat=lat, lng=lng, service="baidu")
            _pano_test(pano_id=pano_id, service="baidu")
        elif "yandex":
            lat, lng = 55.76550473786485, 37.54340745542864
            pano_id = "1298034314_672832338_23_1528540830"
            _pano_test(pano_id=pano_id, service="yandex")
    
    print("\nURL <-> Coordinates Test")
    for service in available_services:
        match service:
            case 'google':
                print("\nGoogle URL test")
                sv_dlp.set_service(service)
                url = "https://goo.gl/maps/c1VXwkHcgj5d7sg16"
                lat, lng = -11.66229059378587, -69.23418815832655
            case 'baidu':
                print("\nBaidu URL test")
                sv_dlp.set_service(service)
                url = "https://map.baidu.com/@11221564.09,2496329.11,21z,87t,-168.01h#panoid=09026600011611300908478628V&panotype=street&heading=76.14&pitch=1.38&l=21&tn=B_NORMAL_MAP&sc=0&newmap=1&shareurl=1&pid=09026600011611300908478628V"
                lat, lng = 39.79019940979819, 116.34668908761401
            case 'yandex':
                print("\nYandex URL Test")
                sv_dlp.set_service(service)
                url = "https://yandex.com/maps/213/moscow/?l=stv%2Csta&ll=37.600082%2C55.790894&mode=search&panorama%5Bdirection%5D=286.651637%2C-5.390625&panorama%5Bfull%5D=true&panorama%5Bid%5D=1298034314_672832338_23_1528540830&panorama%5Bpoint%5D=37.599959%2C55.790842&panorama%5Bspan%5D=105.239256%2C60.000000&sll=37.600050%2C55.790854&text=55.790854%2C37.600050&z=20"
                lat, lng = 41.3432002141999, 69.2646005452
            case _:
                continue
            
        try:
            pano = sv_dlp.get_pano_from_url(url)
            print(pano)
            url = sv_dlp.short_url(pano_id=pano)
            print(url)
            c_url = sv_dlp.short_url(lat=lat, lng=lng)
            print(c_url)
            
        except NameError: # if service not in match segment
            continue