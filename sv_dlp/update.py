import platform
import requests
from urllib.request import urlretrieve
import version

__version__ = version.__version__
SYS_OS = platform.system()
SYS_ARCH = platform.architecture()[0][:2]
SUFFIX = f"sv-dlp{'_macos' if SYS_OS == 'Darwin' else ''}{'_x86' if SYS_ARCH == '32' else ''}{'.exe' if SYS_OS == 'Windows' else ''}"
data = requests.get('https://api.github.com/repos/juanpisuribe13/sv-dlp/releases').json()

def get_lastver():
    return data[0]['tag_name']

def update_program():
    for asset in data[0]["assets"]:
        if asset["name"] == SUFFIX:
            download_url = asset["browser_download_url"]
    urlretrieve(download_url, f"sv-dlp{'.exe' if SYS_OS == 'Windows' else ''}")