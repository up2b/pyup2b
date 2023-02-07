#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: thepoy
# @Email: thepoy@163.com
# @File Name: __init__.py
# @Created:  2021-06-18 11:08:30
# @Modified:  2023-02-07 10:50:30

import os

from pathlib import Path

BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
IMAGES_DIR = BASE_DIR / "images"

IMAGES = [
    IMAGES_DIR / "1.png",
    IMAGES_DIR / "2.jpeg",
    IMAGES_DIR / "3.jpeg",
]
