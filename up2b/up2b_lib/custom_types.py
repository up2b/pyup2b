#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: thepoy
# @Email: thepoy@163.com
# @File Name: custom_types.py
# @Created:  2021-02-09 11:27:21
# @Modified:  2022-03-17 19:13:17

from typing import Dict, List, Union
from dataclasses import dataclass


@dataclass
class ImageStream:
    filename: str
    stream: bytes
    mime_type: str


ImagePath = str
AuthInfo = Dict[str, str]
DeletedResponse = Dict[str, Union[bool, str]]
ImageType = Union[ImagePath, ImageStream]
Images = List[ImageType]
