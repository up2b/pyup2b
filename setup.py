#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: thepoy
# @Email: thepoy@163.com
# @File Name: setup.py
# @Created: 2021-03-27 09:55:27
# @Modified:  2022-03-09 11:39:34

import codecs
import up2b

from setuptools import setup, find_packages

with codecs.open("README.md", "r", "utf-8") as fd:
    setup(
        name="up2b",
        version=up2b.__version__,
        description="""
        A package that can upload images to the image bed in Typora.
        """,
        long_description_content_type="text/markdown",
        long_description=fd.read(),
        author="thepoy",
        author_email="thepoy@163.com",
        url="https://github.com/thep0y/up2b",
        license="MIT",
        keywords="typora image bed upload",
        packages=find_packages(),
        entry_points={"console_scripts": ["up2b = up2b:run_main"]},
        install_requires=[
            "requests",
            "requests-toolbelt",
            "colorful-logger>=0.1.3",
        ],
        extras_require={
            "mark": ["pillow"],
        },
    )
