from collections.abc import Sequence
from pathlib import Path
import requests

from abc import ABC, abstractmethod
from typing import overload, Optional, List, Tuple, Dict, Union
from up2b.up2b_lib.cache import Cache
from up2b.up2b_lib.constants import ImageBedCode
from up2b.up2b_lib.custom_types import (
    ConfigFile,
    DownloadErrorResponse,
    ErrorResponse,
    GitGetAllImagesResponse,
    ImageBedType,
    ImagePath,
    ImageStream,
    ImageType,
    AuthInfo,
    ImgtuResponse,
    SMMSResponse,
    UploadErrorResponse,
)


def choose_image_bed(image_bed_code: int) -> None:
    ...


AllImagesResponse = (
    List[GitGetAllImagesResponse] | List[SMMSResponse] | List[ImgtuResponse]
)


class ImageBedAbstract(ABC):
    @abstractmethod
    def get_all_images(self) -> Union[AllImagesResponse, ErrorResponse]:
        ...

    @abstractmethod
    def upload_image(self, image_path: ImagePath) -> Union[str, UploadErrorResponse]:
        pass

    @abstractmethod
    def upload_image_stream(
        self, image: ImageStream
    ) -> Union[str, UploadErrorResponse]:
        ...

    @overload
    @abstractmethod
    def delete_image(
        self, unique_id: str, retries: int = ...
    ) -> Optional[ErrorResponse]:
        ...

    @overload
    @abstractmethod
    def delete_image(
        self,
        sha: str,
        url: str,
        message: str = ...,
    ) -> Optional[ErrorResponse]:
        ...

    @overload
    @abstractmethod
    def delete_images(
        self, unique_ids: List[str], retries: int = ...
    ) -> Dict[str, ErrorResponse]:
        ...

    @overload
    @abstractmethod
    def delete_images(
        self,
        info: List[Tuple[str, str]],
        message: str = ...,
    ) -> Dict[str, ErrorResponse]:
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        ...


class Base:
    image_bed_code: ImageBedCode
    max_size: int
    conf: ConfigFile
    image_bed_type: ImageBedType
    conf_file: str
    auth_info: Optional[AuthInfo]
    add_watermark: bool
    auto_compress: bool
    ignore_cache: bool
    timeout: float
    cache: Cache

    def __init__(
        self,
        auto_compress: bool = ...,
        add_watermark: bool = ...,
        ignore_cache: bool = ...,
    ) -> None:
        ...

    def check_login(self) -> None:
        ...

    def _read_auth_info(self) -> Optional[AuthInfo]:
        ...

    def _save_auth_info(self, auth_info: Dict[str, str]) -> None:
        ...

    def _exceed_max_size(
        self, images: Tuple[Union[ImageType, DownloadErrorResponse]]
    ) -> Tuple[bool, Optional[str]]:
        ...

    def _check_images_valid(
        self, images: Tuple[Union[ImageType, DownloadErrorResponse]]
    ):
        ...

    def _compress_image(self, image: ImageType) -> ImageType:
        ...

    def _add_watermark(self, image_path: ImagePath) -> ImagePath:
        ...

    def _clear_cache(self) -> None:
        ...

    def _check_cache(self, image: Path) -> Tuple[str, str, bool]:
        ...

    def upload_images(
        self, *images: Union[ImageType, DownloadErrorResponse], to_console: bool = ...
    ) -> List[Union[str, UploadErrorResponse]]:
        ...


class GitBase(Base, ImageBedAbstract):
    headers: Dict[str, str]
    api_url: str

    token: str
    username: str
    repo: str
    folder: str

    def __init__(
        self,
        auto_compress: bool = ...,
        add_watermark: bool = ...,
        ignore_cache: bool = ...,
    ) -> None:
        ...

    def login(self, token: str, username: str, repo: str, folder: str = ...) -> None:
        ...

    def _upload(
        self, image: ImageType, data: Dict[str, str], request_method: str = ...
    ) -> Union[str, UploadErrorResponse]:
        ...

    @abstractmethod
    def _get_all_images_in_image_bed(
        self,
    ) -> requests.Response:
        ...

    def get_all_images(self) -> Union[List[GitGetAllImagesResponse], ErrorResponse]:
        ...

    def _delete_image(
        self,
        sha: str,
        url: str,
        message: str = ...,
        extra: Optional[Dict[str, str]] = ...,
    ) -> Optional[ErrorResponse]:
        ...

    def delete_images(
        self,
        info: List[Tuple[str, str]],
        message: str = ...,
    ) -> Dict[str, ErrorResponse]:
        ...

    @property
    def base_url(self) -> str:
        ...
