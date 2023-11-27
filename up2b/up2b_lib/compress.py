#!/usr/bin/env python3
# -*- coding:utf-8 -*-

try:
    from PIL import Image
except ModuleNotFoundError:
    raise Exception(
        "you have enabled the automatic image compression feature, but [ pillow ] is not installed, please execute `pip install pillow` before enabling this feature"
    )

import os

from io import BytesIO
from pathlib import Path
from up2b.up2b_lib.custom_types import ImageType, CompressedFormat
from up2b.up2b_lib.constants import CACHE_PATH
from up2b.up2b_lib.log import child_logger

logger = child_logger(__name__)


class Compressor:
    def __init__(self, max_size: int, format: CompressedFormat) -> None:
        self.max_size = max_size
        self.format = format

    def compress_to_bytes(self, img: Image.Image, scale: float) -> BytesIO:
        format = img.format
        width, height = img.size
        img_io = BytesIO()

        if format == self.format.value.upper():  # 如果已压缩为 webp 体积仍然很大，对图片进行缩放
            img = img.resize((int(width * scale), int(height * scale)), Image.LANCZOS)

        # TODO: 所有图片都压缩为 webp，动图的压缩可能会报错或被压缩为静态图。
        img.save(img_io, self.format.value)

        new_size = img_io.tell()

        if new_size <= self.max_size:
            return img_io

        scale = self.max_size / new_size
        return self.compress_to_bytes(Image.open(img_io), scale)

    def __call__(self, image: ImageType) -> ImageType:
        raw_size = (
            os.path.getsize(image) if isinstance(image, Path) else len(image.stream)
        )
        if raw_size <= self.max_size:
            return image

        filename = (
            os.path.splitext(os.path.basename(str(image)))[0] + "." + self.format.value
        )
        scale = self.max_size / raw_size
        img = Image.open(image if isinstance(image, Path) else image.stream)

        compressed_img = self.compress_to_bytes(img, scale)
        if not os.path.exists(CACHE_PATH):
            os.mkdir(CACHE_PATH)

        compressed_size = compressed_img.tell()

        img_cache_path = CACHE_PATH / filename
        with img_cache_path.open("wb") as f:
            f.write(compressed_img.getbuffer())

        logger.info(
            "image compression complete",
            image=img_cache_path,
            raw_size=f"{raw_size/1024/1024:.2f}M",
            compressed_size=f"{compressed_size/1024/1024:.2f}M",
        )

        return img_cache_path
