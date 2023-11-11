from setuptools import setup, find_packages
from utils.version import read_file, read_version

VERSION = read_version()
REQUIREMENTS = read_file('requirements.txt').splitlines()
DESCRIPTION = '''
Flexible Street View API Wrapper for Python
'''
LONG_DESCRIPTION = read_file('README.md')

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
)