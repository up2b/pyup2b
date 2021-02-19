#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: thepoy
# @Email: thepoy@aliyun.com
# @File Name: __init__.py
# @Created: 2021-02-13 09:02:21
# @Modified: 2021-02-15 18:53:44

import os
import sys
import json
import shutil
import mimetypes

from io import BytesIO
from typing import Optional, List, Tuple, Dict
from PIL import Image
from timg.timglib import custom_types
from timg.timglib.utils import Login
from timg.timglib.errors import UnsupportedType, OverSizeError

IS_WINDOWS = sys.platform == "win32"

if not IS_WINDOWS:
    TYPORA_APPDATA_PATH = os.path.join(
        os.environ["HOME"],
        ".config",
        "Typora",
    )
else:
    TYPORA_APPDATA_PATH = os.path.join(
        os.environ['APPDATA'],
        "Typora",
    )

CONF_FILE = os.path.join(
    TYPORA_APPDATA_PATH,
    "conf",
    "conf.timg.json",
)


def choose_image_bed(key: str, conf_file: str = CONF_FILE):
    try:
        with open(conf_file, "r+") as f:
            conf = json.loads(f.read())
            f.seek(0, 0)
            conf["image_bed"] = key
            f.write(json.dumps(conf))
            f.truncate()
    except FileNotFoundError:
        with open(conf_file, "w") as f:
            f.write(json.dumps({"image_bed": key}))


class Base:
    def __init__(self, key: str, conf_file: str = CONF_FILE):
        self.conf_file: str = conf_file
        self.max_size: int = 0
        self.auto_compress: bool = False
        self.key: Optional[str] = key
        self.auth_info: Optional[
            custom_types.AuthInfo] = self._read_auth_info()

    def login(self, username: str, password: str):
        pass

    @Login
    def upload_image(self, image_path: str) -> str:
        pass

    @Login
    def upload_images(self, images_path: List[str]):
        pass

    def _read_auth_info(self) -> Optional[custom_types.AuthInfo]:
        try:
            with open(self.conf_file) as f:
                conf = json.loads(f.read())
                return conf["auth_data"][self.key]
        except Exception:
            return None

    def _save_auth_info(self, auth_info: Dict[str, str]):
        try:
            with open(self.conf_file, "r+") as f:
                conf = json.loads(f.read())
                try:
                    conf['auth_data'][self.key] = auth_info
                except KeyError:
                    conf["auth_data"] = {}
                    conf['auth_data'][self.key] = auth_info
                f.seek(0, 0)
                f.write(json.dumps(conf))
                f.truncate()
        except FileNotFoundError:
            print(
                "Error: Auth configure file is not found, "
                "please choose image bed with `--choose-site` or `-c` first.")
            sys.exit(0)
        except Exception as e:
            print(e)

    def _auto_login(self):
        username = self.auth_info["username"]
        password = self.auth_info["password"]
        self.login(username, password)
        self.auth_info = self._read_auth_info()

    def _exceed_max_size(self,
                         *images_path: str) -> Tuple[bool, Optional[str]]:
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
                if os.path.getsize(_img) > self.max_size and _img.split(
                        ".")[-1].lower() not in ["jpg", "png", "jpeg"]:
                    raise UnsupportedType(
                        "currently does not support compression of this type of image: %s"
                        % _img.split(".")[-1].upper())

    def _compress_image(self, image_path: str) -> str:
        if self.auto_compress:
            raw_size = os.path.getsize(image_path)
            if raw_size > self.max_size:

                filename = os.path.basename(image_path).split(".")[0]
                img_mime, _ = mimetypes.guess_type(image_path)
                scale = self.max_size / raw_size
                img = Image.open(image_path)

                def compress(img: Image, scale: float) -> BytesIO:
                    format = img.format
                    width, height = img.size
                    img_io = BytesIO()

                    if format == "PNG":
                        img = img.convert("RGB")
                        img.format = "JPEG"
                        img.save(img_io, "jpeg")
                    elif format == "JPEG":
                        img = img.resize(
                            (int(width * scale), int(height * scale)),
                            Image.ANTIALIAS)
                        img.format = "JPEG"
                        img.save(img_io, "jpeg")
                    else:
                        raise UnsupportedType(
                            "currently does not support compression of this type of image: %s"
                            % format)

                    if img_io.tell() > self.max_size:
                        scale = self.max_size / img_io.tell()
                        return compress(img, scale)
                    return img_io

                if img.format == "PNG":
                    filename += ".jpeg"
                else:
                    filename += "." + img.format.lower()
                img_io = compress(img, scale)
                cache_path = os.path.join(TYPORA_APPDATA_PATH, "Cache", "timg")
                img_cache_path = os.path.join(cache_path, filename)
                try:
                    with open(img_cache_path, "wb") as f:
                        f.write(img_io.getbuffer())
                except FileNotFoundError:
                    os.mkdir(cache_path)
                    with open(img_cache_path, "wb") as f:
                        f.write(img_io.getbuffer())
                return img_cache_path
        return image_path

    def _clear_cache(self):
        cache_path = os.path.join(TYPORA_APPDATA_PATH, "Cache", "timg")
        if os.path.exists(cache_path):
            shutil.rmtree(cache_path)
            os.mkdir(cache_path)
