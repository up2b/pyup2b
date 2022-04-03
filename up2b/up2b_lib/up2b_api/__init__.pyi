import requests

from typing import overload
from abc import ABC, abstractmethod
from typing import Optional, List, Tuple, Dict, Union
from up2b.up2b_lib.custom_types import (
    ConfigFile,
    ErrorResponse,
    GitGetAllImagesResponse,
    ImageBedType,
    ImageStream,
    ImageType,
    AuthInfo,
    UploadErrorResponse,
)


def choose_image_bed(image_bed_code: int) -> None:
    ...


class ImageBedAbstract(ABC):
    @abstractmethod
    def get_all_images(self) -> Union[List[GitGetAllImagesResponse], ErrorResponse]:
        ...

    @abstractmethod
    def upload_image(self, image_path: str) -> Union[str, UploadErrorResponse]:
        ...

    @abstractmethod
    def upload_image_stream(
        self, image: ImageStream
    ) -> Union[str, UploadErrorResponse]:
        ...

    @abstractmethod
    def upload_images(
        self, *images: ImageType, to_console: bool = ...
    ) -> List[Union[str, UploadErrorResponse]]:
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


class Base:
    image_bed_code: int
    max_size: int
    conf: ConfigFile
    image_bed_type: ImageBedType
    conf_file: str
    auth_info: Optional[AuthInfo]
    add_watermark: bool
    auto_compress: bool
    timeout: float

    def __init__(
        self,
        auto_compress: bool = ...,
        add_watermark: bool = ...,
        conf_file: str = ...,
    ) -> None:
        ...

    def check_login(self) -> None:
        ...

    def _read_auth_info(self) -> Optional[AuthInfo]:
        ...

    def _save_auth_info(self, auth_info: Dict[str, str]) -> None:
        ...

    def _exceed_max_size(self, *images: ImageType) -> Tuple[bool, Optional[str]]:
        ...

    def _check_images_valid(self, *images: ImageType):
        ...

    def _compress_image(self, image: ImageType) -> ImageType:
        ...

    def _add_watermark(self, image_path: str) -> str:
        ...

    def _clear_cache(self) -> None:
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
        conf_file: str = ...,
    ) -> None:
        ...

    def login(self, token: str, username: str, repo: str, folder: str = ...) -> None:
        ...

    def _upload(
        self, image: ImageType, data: Dict[str, str], request_method: str = ...
    ) -> Union[str, UploadErrorResponse]:
        ...

    def upload_images(
        self, *images: ImageType, to_console: bool = ...
    ) -> List[Union[str, UploadErrorResponse]]:
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
