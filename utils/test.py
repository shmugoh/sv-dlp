# go a path back to the root directory
import sys
sys.path.insert(0, '..')

import sv_dlp
import unittest

import textwrap
from random import randrange

class TestSvDlp(unittest.TestCase):
    """
    A class that contains unit tests for the sv-dlp library.

    Methods
    -------
    setUp(self)
        Initializes the necessary variables for the tests.
    test_pano_download(self)
        Tests the download of panorama images.
    test_ll_md(self)
        Tests the retrieval of metadata and panorama ID from latitude and longitude coordinates.
    test_url(self)
        Tests the retrieval of panorama ID from a URL and the generation of short URLs.
    """
    def setUp(self):
        """
        Initializes the necessary variables for the tests.
        """
        self.sv_dlp = sv_dlp.sv_dlp()
        self.services = {
            "apple": (37.77499382574212, -122.47185699855395, None),
            "bing": (37.77499382574212, -122.47185699855395, None),
            "google": (37.77499382574212, -122.47185699855395, "YV7i9WYmvPqT5nEtFLq3SA"),
            "baidu": (39.90802391019931, 116.3403752455185, "09026600011611300908478628V"),
            "yandex": (55.76550473786485, 37.54340745542864, "1298034314_672832338_23_1528540830"),
            "naver": (37.5077677, 126.9400753, "wC7zT2RszClsKfYvh4Zcfg")
        }
        self.url_dict = {
            "google": ("https://maps.app.goo.gl/iZVE6N3nTfVfvSTZ6", -11.66229059378587, -69.23418815832655),
            "baidu": ("https://map.baidu.com/@11221564.09,2496329.11,21z,87t,-168.01h#panoid=09026600011611300908478628V&panotype=street&heading=76.14&pitch=1.38&l=21&tn=B_NORMAL_MAP&sc=0&newmap=1&shareurl=1&pid=09026600011611300908478628V", 39.79019940979819, 116.34668908761401),
            "yandex": ("https://yandex.com/maps/213/moscow/?l=stv%2Csta&ll=37.600082%2C55.790894&mode=search&panorama%5Bdirection%5D=286.651637%2C-5.390625&panorama%5Bfull%5D=true&panorama%5Bid%5D=1298034314_672832338_23_1528540830&panorama%5Bpoint%5D=37.599959%2C55.790842&panorama%5Bspan%5D=105.239256%2C60.000000&sll=37.600050%2C55.790854&text=55.790854%2C37.600050&z=20", 41.3432002141999, 69.2646005452),
            "naver": ("https://naver.me/5nPJ8YmO", 37.51939426170934, 126.96017727550505)
        }
        # TODO: Test w/ new URLs instead of Constant, as these expire shortly after.

    def test_pano_download(self):
        """
        Tests the download of panorama images.
        """
        for service, (lat, lng, pano_id) in self.services.items():
            with self.subTest(service=service):
                print(f"Pano Test: {service}")
                try:
                    self.sv_dlp.set_service(service)
                    if service == "apple" or service == "bing":
                        md = self.sv_dlp.get_metadata(lat=lat, lng=lng)
                        pano_id = md.pano_id
                    else:
                        md = self.sv_dlp.get_metadata(pano_id)
                    img = self.sv_dlp.download_panorama(pano_id=pano_id)
                    self.sv_dlp.postdownload.save_panorama(img, md)
                    assert img is not None, "Failed to download panorama"
                except Exception as e:
                    self.fail(f"ERROR: Pano Test - {service}")

    def test_ll_md(self):
        """
        Tests the retrieval of metadata and panorama ID from latitude and longitude coordinates.
        """
        for service, (lat, lng, pano_id) in self.services.items():
            with self.subTest(service=service):
                print(f"LL Test: {service}")
                wrapper = textwrap.TextWrapper(initial_indent=f"{service}: ", width=70, subsequent_indent=' '*8)
                try:
                    self.sv_dlp.set_service(service)
                    md = self.sv_dlp.get_metadata(lat=lat, lng=lng)
                    assert md is not None, "Failed to get panorama ID"
                    print(wrapper.fill(str(md)))
                except Exception as e:
                    self.fail(f"ERROR: LL Test - {service}")

    def test_url(self):
        """
        Tests the retrieval of panorama ID from a URL and the generation of short URLs.
        """
        for service in self.services:
            if service in self.url_dict:
                with self.subTest(service=service):
                    self.sv_dlp.set_service(service)
                    print(f"URL Test: {service}")
                    try:
                        url, lat, lng = self.url_dict[service]
                        pano = self.sv_dlp.get_pano_from_url(url)
                        print(f"Pano from URL: {pano}")
                        assert pano is not None, "Failed to get panorama from URL"
                        
                        url = self.sv_dlp.short_url(pano_id=pano, heading=-randrange(-360, 360), pitch=randrange(-90, 90), zoom=randrange(10, 100))
                        assert url is not None, "Failed to get short URL"
                        print(f"Pano URL: {url}")
                        
                        c_url = self.sv_dlp.short_url(lat=lat, lng=lng, heading=-randrange(-360, 360), pitch=randrange(-90, 90), zoom=randrange(10, 100))
                        assert c_url is not None, "Failed to get short URL from coordinates"
                        print(f"Coordinates URL: {c_url}")
                    except Exception as e:
                        self.fail(f"ERROR: URL Test - {service}")

    def test_service(self):
        """
        Tests Download, Metadata, and URL functions for parsed service.
        """
        import os
        self.service = os.environ["SERVICE"]
        if self.service not in self.services:
            self.fail("Invalid Service")
            
        # Initiate Service & Key Vars
        self.sv_dlp.set_service(self.service)
        lat, lng, pano_id = self.services[self.service]
        
        # Panorama Download Service
        print(f"{self.service} - Panorama Download Service")
        with self.subTest():
            if self.service == "apple" or self.service == "bing":
                md = self.sv_dlp.get_metadata(lat=lat, lng=lng)
                pano_id = md.pano_id
            else:
                md = self.sv_dlp.get_metadata(pano_id)
            img = self.sv_dlp.download_panorama(pano_id=pano_id)
            self.sv_dlp.postdownload.save_panorama(img, md)
            assert img is not None, "Failed to download panorama"                

        # Metadata Service
        print(f"{self.service} - Metadata Service")
        with self.subTest():
            md = self.sv_dlp.get_metadata(lat=lat, lng=lng)
            assert md is not None, "Failed to get metadata"
            print(md)
        
        # URL Service
        print(f"{self.service} - URL Service")
        with self.subTest():
                if self.service not in self.url_dict:
                    self.skipTest(f"{self.service} does not support URL Service")

                url, lat, lng = self.url_dict[self.service]
                pano = self.sv_dlp.get_pano_from_url(url)
                print(f"Pano from URL: {pano}")
                assert pano is not None, "Failed to get panorama from URL"
                
                url = self.sv_dlp.short_url(pano_id=pano, heading=-randrange(-360, 360), pitch=randrange(-90, 90), zoom=randrange(10, 100))
                assert url is not None, "Failed to get short URL"
                print(f"Pano URL: {url}")
                
                c_url = self.sv_dlp.short_url(lat=lat, lng=lng, heading=-randrange(-360, 360), pitch=randrange(-90, 90), zoom=randrange(10, 100))
                assert c_url is not None, "Failed to get short URL from coordinates"
                print(f"Coordinates URL: {c_url}")

if __name__ == '__main__':
    unittest.main()