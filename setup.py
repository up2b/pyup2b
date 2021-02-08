#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: thepoy
# @Email: thepoy@aliyun.com
# @File Name: setup.py
# @Created: 2021-02-08 15:27:43
# @Modified: 2021-02-08 16:56:25

import timg

from setuptools import setup, find_packages

# class Run(Command):
#     user_options = []

#     def initialize_options(self):
#         pass

#     def finalize_options(self):
#         pass

#     def run(self):
#         pass

setup(
    name="typora-upload-image",
    version=timg.__version__,
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'timg = timg:run_main',
        ],
    },
    install_required=[
        "requests",
    ],
)
