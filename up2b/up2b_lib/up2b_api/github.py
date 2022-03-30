#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author:    thepoy
# @Email:     thepoy@163.com
# @File Name: github.py
# @Created:   2021-02-13 09:10:14
# @Modified:  2022-03-30 19:56:34

import os
import requests

from base64 import b64encode
from typing import Optional
from up2b.up2b_lib.custom_types import ImageBedType, ImageStream, ErrorResponse
from up2b.up2b_lib.up2b_api import GitBase
from up2b.up2b_lib.constants import ImageBedCode
from up2b.up2b_lib.utils import child_logger

logger = child_logger(__name__)


class Github(GitBase):
    image_bed_code = ImageBedCode.GITHUB
    max_size = 20 * 1024 * 1024
    api_url = "https://api.github.com"
    image_bed_type = ImageBedType.git

    def __init__(
        self,
        auto_compress: bool = False,
        add_watermark: bool = False,
    ):
        super().__init__(auto_compress, add_watermark)

        if hasattr(self, "token"):
            self.headers = {
                "Accept": "application/vnd.github.v3+json",
                "Authorization": "token " + self.token,
            }

    def upload_image(self, image_path: str):
        basename = os.path.basename(image_path)
        logger.debug("uploading: %s", basename)
        with open(image_path, "rb") as fb:
            data = {
                "content": b64encode(fb.read()).decode("utf-8"),
                "message": "up2b - " + basename,
            }
        return self._upload(image_path, data)

    def upload_image_stream(self, image: ImageStream):
        logger.debug("uploading: %s", image.filename)
        data = {
            "content": b64encode(image.stream).decode("utf-8"),
            "message": "up2b - " + image.filename,
        }
        return self._upload(image, data)

    def _get_all_images_in_image_bed(
        self,
    ):
        resp = requests.get(self.base_url, headers=self.headers, timeout=self.timeout)

        return resp

    def delete_image(
        self,
        sha: str,
        url: str,
        message: str = "Delete pictures that are no longer used",
    ) -> Optional[ErrorResponse]:
        return self._delete_image(sha, url, message)

    def cdn_url(self, url: str) -> str:
        path = url.split("/main/")[-1]
        return "https://cdn.jsdelivr.net/gh/%s/%s/%s" % (self.username, self.repo, path)

    def __repr__(self):
        return "github.com"
