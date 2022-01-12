#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: thepoy
# @Email: thepoy@aliyun.com
# @File Name: __init__.py
# @Created: 2021-02-13 09:02:21
# @Modified:  2022-01-09 11:57:23

import os
import json
import shutil

from io import BytesIO
from abc import ABC, abstractmethod
from typing import Optional, List, Tuple, Dict
from up2b.up2b_lib import custom_types
from up2b.up2b_lib.utils import child_logger
from up2b.up2b_lib.errors import UnsupportedType, OverSizeError
from up2b.up2b_lib.constants import (
    IMAGE_BEDS_CODE,
    CONF_FILE,
    CACHE_PATH,
)

logger = child_logger(__name__)


def choose_image_bed(image_bed_code: int, conf_file: str = CONF_FILE):
    if type(image_bed_code) != int:
        raise TypeError(
            "image bed code must be an integer, not %s" % str(type(image_bed_code))
        )
    try:
        with open(conf_file, "r+") as f:
            conf = json.loads(f.read())
            f.seek(0, 0)
            conf["image_bed"] = image_bed_code
            f.write(json.dumps(conf))
            f.truncate()
    except FileNotFoundError:
        with open(conf_file, "w") as f:
            f.write(json.dumps({"image_bed": image_bed_code}))


class ImageBedMixin(ABC):
    @abstractmethod
    def get_all_images(self) -> List[str]:  # type: ignore
        pass

    @abstractmethod
    def upload_image(self, image_path: str) -> str:  # type: ignore
        pass

    @abstractmethod
    def upload_images(self, images_path: List[str]):
        pass

    @abstractmethod
    def delete_image(
        self,
        sha: str,
        url: str,
        message: str = "Delete pictures that are no longer used",
    ):
        pass

    @abstractmethod
    def delete_images(
        self,
        info: Tuple[str, str],
        message: str = "Delete pictures that are no longer used",
    ):
        pass


class Base:
    image_bed_code: int
    max_size: int

    def __init__(
        self,
        auto_compress: bool = False,
        add_watermark: bool = False,
        conf_file: str = CONF_FILE,
    ):
        self.conf_file: str = conf_file
        self.conf = dict()
        self.auth_info: Optional[custom_types.AuthInfo] = self._read_auth_info()
        self.add_watermark: bool = add_watermark
        if self.add_watermark:
            if not self.conf.get("watermark"):
                logger.fatal(
                    "you have enabled the function of adding watermark, but the watermark is not configured, please configure the text watermark through `--config-text-watermark`"
                )
        self.auto_compress: bool = auto_compress

    def _read_auth_info(self) -> Optional[custom_types.AuthInfo]:
        try:
            with open(self.conf_file) as f:
                self.conf = json.loads(f.read())
                return self.conf["auth_data"][self.image_bed_code]
        except Exception:
            return None

    def _save_auth_info(self, auth_info: Dict[str, str]):
        logger.debug("current image bed code: %d", self.image_bed_code)
        try:
            with open(self.conf_file, "r+") as f:
                conf = json.loads(f.read())
                try:
                    conf["auth_data"][self.image_bed_code] = auth_info
                except KeyError:
                    # 列表不能用 None 填充，要用空字典填充，不然 pyright 会报错
                    conf["auth_data"] = [{}] * len(IMAGE_BEDS_CODE)
                    conf["auth_data"][self.image_bed_code] = auth_info
                f.seek(0, 0)
                f.write(json.dumps(conf))
                f.truncate()
        except FileNotFoundError:
            logger.fatal(
                "auth configure file is not found, please choose image bed with `--choose-site` or `-c` first."
            )
        except Exception as e:
            logger.fatal(e)

    def _exceed_max_size(self, *images_path: str) -> Tuple[bool, Optional[str]]:
        for img in images_path:
            if os.path.getsize(img) > self.max_size:
                return True, img
        return False, None

    def _check_images_valid(self, images_path: List[str]):
        """
        Check if all images exceed the max size or can be compressed
        """
        if not self.auto_compress:
            exceeded, _img = self._exceed_max_size(*images_path)
            if exceeded:
                raise OverSizeError(_img)
        else:
            for _img in images_path:
                if os.path.getsize(_img) > self.max_size and _img.split(".")[
                    -1
                ].lower() not in ["jpg", "png", "jpeg"]:
                    raise UnsupportedType(
                        "currently does not support compression of this type of image: %s"
                        % _img.split(".")[-1].upper()
                    )

    def _compress_image(self, image_path: str) -> str:
        if self.auto_compress:
            from PIL import Image

            raw_size = os.path.getsize(image_path)
            if raw_size > self.max_size:

                filename = os.path.basename(image_path).split(".")[0]
                scale = self.max_size / raw_size
                img = Image.open(image_path)

                def compress(img: Image.Image, scale: float) -> BytesIO:
                    format = img.format
                    width, height = img.size
                    img_io = BytesIO()

                    if format == "PNG":
                        img = img.convert("RGB")
                        img.format = "JPEG"  # type: ignore
                        img.save(img_io, "jpeg")
                    elif format == "JPEG":
                        img = img.resize(
                            (int(width * scale), int(height * scale)), Image.ANTIALIAS
                        )
                        img.format = "JPEG"  # type: ignore
                        img.save(img_io, "jpeg")
                    else:
                        raise UnsupportedType(
                            "currently does not support compression of this type of image: %s"
                            % format
                        )

                    if img_io.tell() > self.max_size:
                        scale = self.max_size / img_io.tell()
                        return compress(img, scale)
                    return img_io

                if img.format == "PNG":
                    filename += ".jpeg"
                else:
                    filename += "." + img.format.lower()  # type: ignore
                img_io = compress(img, scale)

                if not os.path.exists(CACHE_PATH):
                    os.mkdir(CACHE_PATH)

                img_cache_path = os.path.join(CACHE_PATH, filename)
                with open(img_cache_path, "wb") as f:
                    f.write(img_io.getbuffer())

                return img_cache_path
        return image_path

    def _add_watermark(self, image_path: str) -> str:
        if self.add_watermark:
            from up2b.up2b_lib.watermark import AddWatermark, TypeFont

            conf = self.conf["watermark"]
            aw = AddWatermark(conf["x"], conf["y"], conf["opacity"])
            return aw.add_text_watermark(
                image_path,
                [TypeFont(conf["text"], conf["size"], conf["font"], (0, 0, 0))],
            )
        return image_path

    def _clear_cache(self):
        if os.path.exists(CACHE_PATH):
            shutil.rmtree(CACHE_PATH)
            os.mkdir(CACHE_PATH)
