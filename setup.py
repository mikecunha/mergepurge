from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path


here = path.abspath(path.dirname(__file__))


def open_file(fname):
    return open(path.join(here, fname), encoding='utf-8')


setup(
    name='mergepurge',
    version='0.1.0',
    description='A package to merge contacts/accounts and purge duplicates.',
    long_description=open_file('README.rst').read(),
    url='https://github.com/mikecunha/mergepurge',
    author='Mike Cunha',
    license=open('LICENSE.txt').read(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows :: Windows 7',
        'Programming Language :: Python :: 3.4',
    ],
    packages=['mergepurge'],
    install_requires=['pandas', 'usaddress', 'probablepeople', 'numpy',
                      'fuzzywuzzy'],

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    #extras_require={
    #    'dev': ['check-manifest'],
    #    'test': ['coverage'],
    #},

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    #package_data={
    #    'sample': ['package_data.dat'],
    #},

)
