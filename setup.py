#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: thepoy
# @Email: thepoy@aliyun.com
# @File Name: setup.py
# @Created: 2021-02-08 15:27:43
# @Modified: 2021-02-13 20:24:04

import codecs
import timg

from setuptools import setup, find_packages

with codecs.open("README.md", "r", "utf-8") as fd:
    setup(
        name="typora-upload-image",
        version=timg.__version__,
        description='''
        A package that can upload images to the image bed in Typora.
        ''',
        long_description_content_type="text/markdown",
        long_description=fd.read(),
        author="thepoy",
        author_email="thepoy@163.com",
        url="https://github.com/thep0y/timg",
        license="MIT",
        keywords="typora image bed upload",
        packages=find_packages(),
        entry_points={
            'console_scripts': [
                'timg = timg:run_main',
            ],
        },
        install_requires=[
            "requests",
            "requests-toolbelt",
        ],
    )
