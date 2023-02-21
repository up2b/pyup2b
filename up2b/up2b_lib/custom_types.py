#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author:      thepoy
# @Email:       thepoy@163.com
# @File Name:   custom_types.py
# @Created At:  2021-02-09 11:27:21
# @Modified At: 2023-02-21 12:41:21
# @Modified By: thepoy

from enum import IntEnum
from typing import Any, Dict, List, Union
from dataclasses import dataclass, asdict
from pathlib import Path


class ImageBedType(IntEnum):
    common = 1
    git = 2


@dataclass
class ImageStream:
    filename: str
    stream: bytes
    mime_type: str

    def __repr__(self) -> str:
        return self.filename


ImagePath = Path
AuthInfo = Dict[str, Any]
AuthData = Dict[str, AuthInfo]
WaterMarkConfig = Dict[str, int]
ConfigFile = Dict[str, Union[int, AuthData, WaterMarkConfig]]
DeletedResponse = Dict[str, Union[bool, str]]
ImageType = Union[ImagePath, ImageStream]
Images = List[ImageType]


@dataclass
class BaseResponse:
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ErrorResponse(BaseResponse):
    status_code: int
    error: Union[str, Dict[str, Any]]


@dataclass
class DownloadErrorResponse(ErrorResponse):
    pass


@dataclass
class UploadErrorResponse(ErrorResponse):
    image_path: str


@dataclass
class GitGetAllImagesResponse(BaseResponse):
    url: str
    sha: str
    delete_url: str


@dataclass
class SMMSResponse(BaseResponse):
    url: str
    delete_url: str
    width: int
    height: int


@dataclass
class CodingResponse(BaseResponse):
    url: str
    filename: str


@dataclass
class ImgtuResponse(BaseResponse):
    id: str
    url: str
    display_url: str
    width: int
    height: int
