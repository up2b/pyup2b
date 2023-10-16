import mimetypes

from typing import Optional, Tuple, BinaryIO, Union
from pathlib import Path
from up2b.up2b_lib.custom_types import ImageType


class File:
    def __init__(
        self, key: str, image: ImageType, filename: Optional[str] = None
    ) -> None:
        self.__key = key

        self.mime_type = (
            mimetypes.guess_type(image)[0]
            if isinstance(image, Path)
            else image.mime_type
        )

        self.filename = (
            filename or image.name if isinstance(image, Path) else image.filename
        )
        self.image = image

    @property
    def key(self):
        return self.__key

    def to_tuple(self) -> Tuple[str, Union[BinaryIO, bytes], str]:
        return (
            self.filename,
            self.image.open("rb")
            if isinstance(self.image, Path)
            else self.image.stream,
            self.mime_type,  # type: ignore
        )

    def to_dict(self):
        return {self.key: self.to_tuple()}
