# 1. Upload to PyPI:
# (Note: Building 'bdist_wheel' requires package 'wheel')
# python3 setup.py sdist bdist_wheel
# twine upload dist/*
#
# 2. Check if everything looks all right: https://pypi.python.org/pypi/textcomplexity
#
# 3. Go to
# https://github.com/tsproisl/textcomplexity/releases/new
# and create a new release

from os import path
from setuptools import setup

version = {}
with open("textcomplexity/version.py") as fh:
    exec(fh.read(), version)

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst')) as fh:
    long_description = fh.read()

setup(
    name='textcomplexity',
    version=version["__version__"],
    author='Thomas Proisl',
    author_email='thomas.proisl@fau.de',
    packages=[
        'textcomplexity',
        'textcomplexity.utils',
    ],
    scripts=[
        'bin/txtcomplexity',
    ],
    package_data={
        "textcomplexity": ["de.json",
                           "en.json"]
    },
    url="https://github.com/tsproisl/textcomplexity",
    download_url='https://github.com/tsproisl/textcomplexity/archive/v%s.tar.gz' % version["__version__"],
    license='GNU General Public License v3 or later (GPLv3+)',
    description="Linguistic and stylistic complexity measures for text",
    long_description=long_description,
    install_requires=[
        "networkx",
        "nltk",
        "nltk_tgrep",
        "numpy",
        "scipy",
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Text Processing :: Linguistic',
    ],
)
