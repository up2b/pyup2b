#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author:    thepoy
# @Email:     thepoy@163.com
# @File Name: test_upload.py
# @Created:   2022-09-02 09:17:46
# @Modified:  2023-02-08 17:46:09

import os
import json
import mimetypes
import requests
import pytest

from typing import Union
from multiprocessing import Process
from pathlib import Path
from tests import IMAGES
from up2b.up2b_lib.errors import OverSizeError
from up2b.up2b_lib.up2b_api import Base
from up2b.up2b_lib.custom_types import (
    ImageBedType,
    ImageType,
    ImageStream,
    ImagePath,
    UploadErrorResponse,
)
from up2b.up2b_lib.constants import ImageBedCode
from tests.server import run_server


class ImageBed(Base):
    image_bed_type = ImageBedType.common
    image_bed_code = ImageBedCode.IMGTG
    max_size = 50 * 1024
    base_url = "http://localhost:8000/"

    def __upload(self, image: ImageType, retries=0) -> Union[str, UploadErrorResponse]:
        image = self._compress_image(image)

        if isinstance(image, Path):
            image = self._add_watermark(image)

        filename_with_suffix = os.path.basename(str(image))
        filename_without_suffix, suffix = os.path.splitext(filename_with_suffix)
        if isinstance(image, Path):
            if suffix.lower() == ".apng":
                suffix = ".png"
            filename = filename_without_suffix + suffix
        else:
            filename = filename_with_suffix + "." + image.mime_type

        mime_type = (
            mimetypes.guess_type(image)[0]
            if isinstance(image, Path)
            else image.mime_type
        )

        if isinstance(image, Path):
            with open(image, "rb") as fb:
                img_buffer = fb.read()
        else:
            img_buffer = image.stream

        files = {
            "source": (filename, img_buffer, mime_type),
        }

        resp = requests.post(
            self.base_url, files=files, timeout=self.timeout  # type: ignore
        )
        resp.encoding = "utf-8"

        try:
            json_resp = resp.json()
        except json.decoder.JSONDecodeError:
            return UploadErrorResponse(resp.status_code, resp.text, str(image))

        return json_resp["url"]

    def upload_image(self, image_path: ImagePath) -> Union[str, UploadErrorResponse]:
        image_path = self._add_watermark(image_path)

        if self.auto_compress:
            # 输入的是路径，返回的也必然是路径，忽略 pyright 的错误提示
            image_path = self._compress_image(image_path)  # type: ignore

        return self.__upload(image_path)

    def upload_image_stream(
        self, image: ImageStream
    ) -> Union[str, UploadErrorResponse]:
        if self.auto_compress:
            new_image = self._compress_image(image)
        else:
            new_image = image

        return self.__upload(new_image)

    def delete_image(self):
        pass

    def delete_images(self):
        pass

    def get_all_images(self):
        pass

    @property
    def description(self):
        return ""


t = Process(target=run_server)
t.daemon = True
t.start()


class TestUpload:
    ib = ImageBed()

    def test_upload(self):
        resp = self.ib.upload_image(IMAGES[0])
        assert resp == "http://localhost:8000/images/1.png"

    def test_check_images(self):
        with pytest.raises(OverSizeError):
            self.ib._check_images_valid(IMAGES)