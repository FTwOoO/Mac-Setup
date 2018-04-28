#!/usr/bin/env python3

import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md'), encoding='utf-8').read()

setup(
    name='msetup',
    version='0.5',

    author='booopooob@gmail.com',
    author_email='booopooob@gmail.com',
    url='https://github.com/FTwO-O/mac-setup',
    license='MIT',

    description="forward the encrpted socks5 data to bypass firewall",
    keywords="mac setup",

    long_description=README,

    packages=find_packages(),

    package_data={
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.md', '*.pac', '*.dylib', '*.so'],
        # And include any *.msg files found in the 'hello' package, too:
    },

    install_requires=[],

    platforms='any',
    include_package_data = True,
    classifiers=[
        "Development Status :: beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Topic :: Internet",
        "Topic :: Utilities"
    ],

     entry_points="""
    [console_scripts]
    msetup = msetup:main
    """,

)