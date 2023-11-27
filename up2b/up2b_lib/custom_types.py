#!/usr/bin/env python3

from enum import Enum, IntEnum
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, asdict
from pathlib import Path

from up2b.up2b_lib.constants import ImageBedCode


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
DeletedResponse = Dict[str, Union[bool, str]]
ImageType = Union[ImagePath, ImageStream]
Images = List[ImageType]


@dataclass
class WaterMarkConfig:
    x: int
    y: int
    text: str
    font: str
    size: int
    opacity: Optional[int] = None

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "WaterMarkConfig":
        return WaterMarkConfig(
            data["x"],
            data["y"],
            data["text"],
            data["font"],
            data["size"],
            data["opacity"],
        )


ConfigFile = Dict[str, Union[int, AuthData, WaterMarkConfig]]


@dataclass
class Config:
    image_bed: Optional[ImageBedCode]
    auth_data: Dict[ImageBedCode, Dict[str, str]]
    watermark: Optional[WaterMarkConfig] = None


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


class CompressedFormat(Enum):
    WEBP = "webp"
    JPEG = "jpeg"
