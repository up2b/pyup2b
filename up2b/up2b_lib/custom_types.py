#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author:    thepoy
# @Email:     thepoy@163.com
# @File Name: custom_types.py
# @Created:   2021-02-09 11:27:21
# @Modified:  2022-03-25 11:20:42

from enum import Enum
from typing import Dict, List, Union
from dataclasses import dataclass, asdict


class ImageBedType(Enum):
    common = 1
    git = 2


@dataclass
class ImageStream:
    filename: str
    stream: bytes
    mime_type: str

    def __repr__(self) -> str:
        return self.filename


ConfigFile = Dict[str, Union[int, List[Dict[str, str]], Dict[str, int]]]
ImagePath = str
AuthInfo = Dict[str, str]
DeletedResponse = Dict[str, Union[bool, str]]
ImageType = Union[ImagePath, ImageStream]
Images = List[ImageType]


@dataclass
class ErrorResponse:
    status_code: int
    error: Union[str, dict]

    def to_dict(self) -> Dict[str, Union[str, int]]:
        return asdict(self)


@dataclass
class UploadErrorResponse(ErrorResponse):
    image_path: str


@dataclass
class GitGetAllImagesResponse:
    url: str
    sha: str
    delete_url: str

    def to_dict(self) -> Dict[str, str]:
        return asdict(self)


@dataclass
class SMMSResponse:
    url: str
    delete_url: str
    width: int
    height: int

    def to_dict(self):
        return asdict(self)


@dataclass
class ImgtuResponse:
    id: str
    url: str
    display_url: str
    width: int
    height: int

    def to_dict(self):
        return asdict(self)
