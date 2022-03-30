#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author:    thepoy
# @Email:     thepoy@163.com
# @File Name: sm.py
# @Created:   2021-02-13 09:04:07
# @Modified:  2022-03-30 19:47:48

import re
import requests

from typing import BinaryIO, List, Optional, Dict, Any, Tuple, Union
from up2b.up2b_lib.custom_types import (
    ErrorResponse,
    ImageBedType,
    ImagePath,
    ImageStream,
    ImageType,
    SMMSResponse,
    UploadErrorResponse,
)
from up2b.up2b_lib.up2b_api import Base, ImageBedAbstract
from up2b.up2b_lib import errors
from up2b.up2b_lib.constants import ImageBedCode
from up2b.up2b_lib.utils import check_image_exists, child_logger

logger = child_logger(__name__)


class SM(Base, ImageBedAbstract):
    image_bed_type = ImageBedType.common
    image_bed_code = ImageBedCode.SM_MS
    base_url = "https://sm.ms/api/v2/"
    max_size = 5 * 1024 * 1024

    def __init__(
        self,
        auto_compress: bool = False,
        add_watermark: bool = False,
    ):
        super().__init__(auto_compress, add_watermark)

        if self.auth_info:
            self.token: str = self.auth_info["token"]

            self.headers = {
                "Authorization": self.token,
            }

    def login(self, username: str, password: str) -> bool:
        try:
            token = self._get_api_token(username, password)
            self._save_auth_info(
                {"token": token, "username": username, "password": password}
            )
            return True
        except Exception as e:
            logger.error(e)
            return False

    def _auto_login(self):
        if not self.auth_info:
            raise ValueError("auth info is not found")

        username = self.auth_info["username"]
        password = self.auth_info["password"]
        self.login(username, password)
        self.auth_info = self._read_auth_info()

        assert self.auth_info is not None

    def _get_api_token(self, username: str, password: str) -> str:
        url = self._url("token")
        data = {"username": username, "password": password}
        resp = requests.post(url, data=data, timeout=self.timeout).json()
        return resp["data"]["token"]

    def _get_user_profile(self) -> Optional[Dict[str, str]]:
        url = self._url("profile")
        resp = requests.post(url, headers=self.headers, timeout=self.timeout).json()
        if resp["success"]:
            return resp["data"]
        else:
            if self._login_expired(resp):
                self._auto_login()
                self.token = self.auth_info["token"]  # type: ignore
        return None

    def __upload(self, image: ImageType, retries=0) -> Union[str, UploadErrorResponse]:
        self.check_login()

        logger.debug("uploading: %s", image)

        image = self._compress_image(image)

        if isinstance(image, str):
            image = self._add_watermark(image)

        # sm.ms不管出不出错，返回的状态码都是200
        url = self._url("upload")
        files: Dict[str, Union[Tuple[str, bytes, str], BinaryIO]] = (
            {"smfile": open(image, "rb")}
            if isinstance(image, str)
            else {"smfile": (image.filename, image.stream, image.mime_type)}
        )

        resp = requests.post(
            url, headers=self.headers, files=files, timeout=self.timeout
        ).json()
        if resp["success"]:
            uploaded_url: str = resp["data"]["url"]
            logger.debug(
                "uploaded: '%s' => '%s'",
                image,
                uploaded_url,
            )
            return uploaded_url
        else:
            if resp["code"] == "image_repeated":
                # 如果图片重复，会返回重复的图片的链接，所以此处不报错
                logger.info("repeated image: %s", resp["images"])
                image_url: str = resp["images"]
                return image_url
            elif self._login_expired(resp):
                assert self.auth_info is not None

                if retries >= 3:
                    return UploadErrorResponse(401, "认证信息无效", str(image))

                logger.warn(
                    "`auth_token` has expired, the program will try to update `auth_token` automatically, number of retries: %d",
                    retries + 1,
                )

                self._auto_login()
                assert self.auth_info is not None
                self.token = self.auth_info["token"]

                return self.__upload(image, retries + 1)
            else:
                error = resp["message"]
                logger.error(
                    "upload failed: img='%s', error='%s'",
                    image,
                    error,
                )
                return UploadErrorResponse(400, error, str(image))

    def upload_image(self, image_path: ImagePath):
        return self.__upload(image_path)

    def upload_image_stream(self, image: ImageStream):
        return self.__upload(image)

    def upload_images(
        self, *images: ImageType, to_console=True
    ) -> List[Union[str, UploadErrorResponse]]:
        self.check_login()

        if len(images) > 10:
            raise errors.OverSizeError(
                "You can only upload up to 10 pictures, but you uploaded %d pictures."
                % len(images)
            )

        check_image_exists(*images)

        self._check_images_valid(*images)

        images_url: List[Union[str, UploadErrorResponse]] = []
        for img in images:
            if isinstance(img, str):
                result = self.upload_image(img)
            else:
                result = self.upload_image_stream(img)

            images_url.append(result)

        if to_console:
            for i in images_url:
                print(i)

        self._clear_cache()

        return images_url

    def history(self) -> Dict[str, Any]:
        """
        Temporary History - IP Based Temporary Upload History
        """
        self.check_login()

        url = self._url("history")
        resp = requests.get(url, headers=self.headers, timeout=self.timeout)
        return resp.json()

    def clear(self) -> Dict[str, Any]:
        """
        Clear Temporary History - Clear IP Based Temporary Upload History
        """
        self.check_login()

        url = self._url("clear")
        resp = requests.get(url, headers=self.headers, timeout=self.timeout)
        return resp.json()

    def upload_history(self) -> Union[ErrorResponse, List[Dict[str, Any]]]:
        self.check_login()

        url = self._url("upload_history")
        resp = requests.get(url, headers=self.headers, timeout=self.timeout).json()
        if resp["code"] != "success":
            if resp["code"] == "unauthorized":
                return ErrorResponse(401, resp["message"])
            else:
                return ErrorResponse(0, resp)
        return resp["data"]

    def get_all_images(self):
        self.check_login()

        images: List[SMMSResponse] = []
        data = self.upload_history()
        if isinstance(data, ErrorResponse):
            return data

        for file in data:
            images.append(
                SMMSResponse(
                    file["url"],
                    file["delete"],
                    file["width"],
                    file["height"],
                )
            )

        return images

    def delete_image(self, delete_url: str) -> Optional[ErrorResponse]:
        self.check_login()

        resp = requests.get(delete_url, timeout=self.timeout)

        re_res = re.search(r'<div class="card-body">\n\s+(.*?)\n', resp.text)
        if not re_res:
            return ErrorResponse(500, "未知错误")

        msg = re_res.group(1)
        if msg == "File is deleted and our cache will refresh within minutes.":
            return ErrorResponse(400, "图片已被删除，请耐心等待服务器刷新缓存")

        if msg == "Picture was already deleted.":
            return ErrorResponse(404, "图片已被删除，请勿重复删除")
        else:
            return ErrorResponse(0, msg)

    def delete_images(self, urls: List[str]) -> Dict[str, ErrorResponse]:
        self.check_login()

        result: Dict[str, ErrorResponse] = {}
        for url in urls:
            r = self.delete_image(url)
            if r:
                result[url] = r
        return result

    def get_all_images_in_image_bed(self) -> List[str]:  # type: ignore
        pass

    def _url(self, path: str) -> str:
        return self.base_url + path

    def _login_expired(self, resp: dict):
        return resp["message"] == "Get user profile failed, invalid Authorization."

    def __repr__(self):
        return "sm.ms"
