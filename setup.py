#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author:    thepoy
# @Email:     thepoy@163.com
# @File Name: setup.py
# @Created:   2021-03-27 09:55:27
# @Modified:  2022-03-25 11:56:28

import codecs
import up2b

from setuptools import setup


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
        packages=["up2b", "up2b.up2b_lib", "up2b.up2b_lib.up2b_api"],
        package_data={
            "up2b": ["py.typed"],
            "up2b.up2b_lib": ["py.typed"],
            "up2b.up2b_lib.up2b_api": ["py.typed", "__init__.pyi"],
        },
        entry_points={"console_scripts": ["up2b = up2b:run_main"]},
        install_requires=[
            "requests",
            "colorful-logger>=0.1.5",
        ],
        extras_require={
            "mark": ["pillow"],
        },
    )
