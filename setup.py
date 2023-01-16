from setuptools import setup, find_packages
from dev_scripts.version_utils import read_file, read_version

VERSION = read_version()
REQUIREMENTS = read_file('requirements.txt').splitlines()
DESCRIPTION = '''
Obtain Street View panoramas, scrape metadata, and generate short URLs for panoramas from multiple Street View services
'''
LONG_DESCRIPTION = read_file('README.md')

setup(
    name='sv-dlp',
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',

    url='https://github.com/juanpisss/sv-dlp',
    maintainer="juanpisss",
    maintainer_email="juanpiss@basedtakes.co",

    packages=find_packages(exclude=('dev_scripts')),
    python_requires='>=3.10', # thinking about making it 3.8
    install_requires=REQUIREMENTS,
)