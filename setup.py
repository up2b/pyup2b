#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: thepoy
# @Email: thepoy@aliyun.com
# @File Name: setup.py
# @Created: 2021-02-08 15:27:43
# @Modified: 2021-02-08 22:43:11

import timg

from setuptools import setup, find_packages

with open("README.md", "r", "utf-8") as f:
    setup(
        name="typora-upload-image",
        version=timg.__version__,
        description='''
        A module that can upload pictures to the image bed in Typora.
        ''',
        long_description=f.read(),
        author="thepoy",
        packages=find_packages(),
        entry_points={
            'console_scripts': [
                'timg = timg:run_main',
            ],
        },
        install_requires=[
            "requests",
        ],
    )
