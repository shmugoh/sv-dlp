from setuptools import setup, find_packages, Distribution
from setuptools.command.build_ext import build_ext
from utils.version import read_file, read_version
import platform

VERSION = read_version()
REQUIREMENTS = read_file('requirements.txt').splitlines()
DESCRIPTION = '''
Flexible Street View API Wrapper for Python
'''
LONG_DESCRIPTION = read_file('README.md')

# Define the data files to include
data_files = []

# Get the current platform
current_platform = platform.system()

# Include the appropriate binary
if current_platform == "Windows":
    data_files.append(('bin', ['dist/bin/sv-dlp.exe']))
elif current_platform == "Linux":
    data_files.append(('bin', ['dist/bin/sv-dlp']))
elif current_platform == "Darwin":
    data_files.append(('bin', ['dist/bin/sv-dlp']))

class BinaryDistribution(Distribution):
    def has_ext_modules(self):
        return True

setup(
    name='sv-dlp',
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',

    url='https://github.com/shmugoh/sv-dlp',
    maintainer="shmugo",
    maintainer_email="juan@shmugo.co",

    packages=find_packages(exclude=('utils')),
    python_requires='>=3.10', # thinking about making it 3.8
    install_requires=REQUIREMENTS,
    include_package_data=True,
    data_files=data_files,  # Add the data files
    distclass=BinaryDistribution,
)