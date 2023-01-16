@REM genuinely the most rockiest programming i've done
@echo OFF
@echo Google Download
py -Werror -Xdev -m "sv_dlp" 71xi-VgKXBBw5LvUWZMzfQ --service google
py -Werror -Xdev -m "sv_dlp" 37.77499382574212, -122.47185699855395 --service google
@echo Google Metadata Test
py -Werror -Xdev -m "sv_dlp" 71xi-VgKXBBw5LvUWZMzfQ --get-m --service google
py -Werror -Xdev -m "sv_dlp" 37.77499382574212, -122.47185699855395 --get-m --service google
@echo Apple Download
py -Werror -Xdev -m "sv_dlp" 37.77499382574212, -122.47185699855395 --service apple
@echo Apple Metadata Test
py -Werror -Xdev -m "sv_dlp" 37.77499382574212, -122.47185699855395 --get-m --service apple
@echo Bing Download
py -Werror -Xdev -m "sv_dlp" 37.77499382574212, -122.47185699855395 --service bing
@echo Bing Metadata Test
py -Werror -Xdev -m "sv_dlp" 37.77499382574212, -122.47185699855395 --get-m --service bing

@REM Baidu Service Test
@echo Baidu Download
py -Werror -Xdev -m "sv_dlp" 39.90802391019931, 116.3403752455185 --service baidu
@echo Baidu Metadata Test
py -Werror -Xdev -m "sv_dlp" 39.90802391019931, 116.3403752455185 --get-m --service baidu

@REM Yandex Service Test
@echo Yandex Download
py -Werror -Xdev -m "sv_dlp" 55.76550473786485, 37.54340745542864 --service yandex
@echo Yandex Metadata Test
py -Werror -Xdev -m "sv_dlp" 55.76550473786485, 37.54340745542864 --get-m --service yandex

@REM Google Short Link Test
@echo Google Short Link Test
py -Werror -Xdev -m "sv_dlp" 71xi-VgKXBBw5LvUWZMzfQ -l
py -Werror -Xdev -m "sv_dlp" 1.62097345657655 -75.61895756809007 -l
py -Werror -Xdev -m "sv_dlp" https://goo.gl/maps/ebd71LHjZWF6HC3AA -p