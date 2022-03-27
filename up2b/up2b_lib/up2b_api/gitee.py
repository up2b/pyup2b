#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author:    thepoy
# @Email:     thepoy@163.com
# @File Name: gitee.py
# @Created:   2021-02-13 09:10:05
# @Modified:  2022-03-27 22:09:15

import os
from typing import Optional
import requests

from base64 import b64encode
from up2b.up2b_lib.custom_types import ImageBedType, ImageStream, ErrorResponse
from up2b.up2b_lib.up2b_api import GitBase
from up2b.up2b_lib.constants import GITEE
from up2b.up2b_lib.utils import child_logger

logger = child_logger(__name__)


class Gitee(GitBase):
    image_bed_code = GITEE
    max_size = 1 * 1024 * 1024
    headers = {"Content-Type": "application/json;charset=UTF-8"}
    api_url = "https://gitee.com/api/v5"
    image_bed_type = ImageBedType.git

    def upload_image(self, image_path: str):
        basename = os.path.basename(image_path)
        logger.debug("uploading: %s", basename)
        with open(image_path, "rb") as fb:
            data = {
                "access_token": self.token,
                "content": b64encode(fb.read()).decode("utf-8"),
                "message": "up2b - " + os.path.basename(basename),
            }
        return self._upload(image_path, data, "post")

    def upload_image_stream(self, image: ImageStream):
        logger.debug("uploading: %s", image.filename)
        data = {
            "access_token": self.token,
            "content": b64encode(image.stream).decode("utf-8"),
            "message": "up2b - " + os.path.basename(image.filename),
        }
        return self._upload(image, data, "post")

    def _get_all_images_in_image_bed(
        self,
    ):
        self.check_login()

        data = {"access_token": self.token}
        resp = requests.get(
            self.base_url, headers=self.headers, json=data, timeout=self.timeout
        )

        return resp

    def delete_image(
        self,
        sha: str,
        url: str,
        message: str = "Delete pictures that are no longer used",
    ) -> Optional[ErrorResponse]:
        extra = {"access_token": self.token}

        return self._delete_image(sha, url, message, extra)

    def __repr__(self):
        return "gitee.com"
