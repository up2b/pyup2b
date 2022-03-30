#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author:    thepoy
# @Email:     thepoy@163.com
# @File Name: imgtu.py
# @Created:   2021-02-13 09:04:37
# @Modified:  2022-03-30 19:56:28

import os
import re
import time
import json
import mimetypes
import requests

from urllib import parse
from typing import Dict, List, Optional, Tuple, Union
from up2b.up2b_lib.custom_types import (
    ErrorResponse,
    ImageBedType,
    ImageType,
    ImageStream,
    ImagePath,
    ImgtuResponse,
    UploadErrorResponse,
)
from up2b.up2b_lib.errors import MissingAuth
from up2b.up2b_lib.up2b_api import Base, ImageBedAbstract
from up2b.up2b_lib.utils import check_image_exists, child_logger
from up2b.up2b_lib.constants import ImageBedCode

logger = child_logger(__name__)


class Imgtu(Base, ImageBedAbstract):
    image_bed_type = ImageBedType.common
    image_bed_code = ImageBedCode.IMGTU
    max_size = 10 * 1024 * 1024
    base_url = "https://imgtu.com/"
    __headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }

    def __init__(
        self,
        auto_compress: bool = False,
        add_watermark: bool = False,
    ):
        super().__init__(auto_compress, add_watermark)

        self.cookie: Optional[str] = None
        self.token: Optional[str] = None
        if self.auth_info:
            self.cookie = self.auth_info["cookie"]
            self.token = self.auth_info["token"]
            self.username = self.auth_info["username"]
            self.__headers["Cookie"] = self.cookie

    def login(self, username: str, password: str) -> bool:
        url = self._url("login")
        auth_token, cookie = self._parse_auth_token()

        if not auth_token or not cookie:
            raise MissingAuth("auth token or cookie is None")

        headers = self.__headers.copy()
        headers["Cookie"] = cookie

        data = {
            "login-subject": username,
            "password": password,
            "auth_token": auth_token,
        }

        resp = requests.post(
            url, headers=headers, data=data, allow_redirects=False, timeout=self.timeout
        )
        if resp.status_code == 301:
            # If there is a KEEPLOGIN field in the cookie,
            # pictures will be uploaded as a normal user
            self.cookie = cookie + "; " + resp.headers["Set-Cookie"].split("; ")[0]

            # If there is no KEEPLOGIN field in the cookie,
            # pictures will be uploaded as a tourist
            # self.cookie = cookie

            auth_info = {
                "token": auth_token,
                "cookie": self.cookie,
                "username": username,
                "password": password,
            }
            self._save_auth_info(auth_info)
            return True

        return False

    def _parse_auth_token(self) -> Tuple[Optional[str], Optional[str]]:
        url = self._url("login")
        resp = requests.get(url, headers=self.__headers, timeout=self.timeout)
        if resp.status_code == 200:
            auth_token = re.search(
                r'PF.obj.config.auth_token = "([a-f0-9]{40})"', resp.text
            )
            if not auth_token:
                return None, None
            resp_set_cookie = resp.headers["Set-Cookie"].split("; ")[0]
            return auth_token.group(1), resp_set_cookie
        else:
            logger.error("response error: status_code=%d", resp.status_code)
            return None, None

    @property
    def headers(self):
        assert self.cookie != None

        headers = self.__headers.copy()
        headers.update(
            {
                "Cookie": self.cookie,
            }
        )
        return headers

    def _update_auth_token(self):
        resp = requests.get(self.base_url, headers=self.headers, timeout=self.timeout)
        auth_token = re.search(
            r'PF.obj.config.auth_token = "([a-f0-9]{40})"', resp.text
        )

        assert auth_token != None

        auth_token = auth_token.group(1)
        if not self.auth_info:
            self.auth_info = {}

        self.auth_info["token"] = self.token = auth_token
        self._save_auth_info(self.auth_info)

    def __upload(self, image: ImageType, retries=0) -> Union[str, UploadErrorResponse]:
        self.check_login()

        image = self._compress_image(image)

        if isinstance(image, str):
            image = self._add_watermark(image)

        url = self._url("json")
        filename_with_suffix = os.path.basename(str(image))
        filename_without_suffix, suffix = os.path.splitext(filename_with_suffix)
        if isinstance(image, str):
            if suffix.lower() == ".apng":
                suffix = ".png"
            filename = filename_without_suffix + suffix
        else:
            filename = filename_with_suffix + "." + image.mime_type

        mime_type = (
            mimetypes.guess_type(image)[0]
            if isinstance(image, str)
            else image.mime_type
        )

        timestamp = int(time.time() * 1000)

        if isinstance(image, str):
            with open(image, "rb") as fb:
                img_buffer = fb.read()
        else:
            img_buffer = image.stream

        data = {
            "type": "file",
            "action": "upload",
            "timestamp": str(timestamp),
            "auth_token": self.token,
            "nsfw": "0",
        }

        files = {
            "source": (filename, img_buffer, mime_type),
        }

        resp = requests.post(
            url, headers=self.headers, data=data, files=files, timeout=self.timeout
        )
        resp.encoding = "utf-8"

        try:
            json_resp = resp.json()
        except json.decoder.JSONDecodeError:
            return UploadErrorResponse(resp.status_code, resp.text, str(image))

        try:
            uploaded_url: str = json_resp["image"]["image"]["url"]
            logger.debug(
                "uploaded url: '%s' => '%s'",
                image,
                uploaded_url,
            )

            return uploaded_url
        except KeyError:
            if json_resp["error"]["message"] == "请求被拒绝 (auth_token)":
                if retries >= 3:
                    return UploadErrorResponse(
                        resp.status_code, resp.json()["error"]["message"], str(image)
                    )

                logger.warn(
                    "`auth_token` has expired, the program will try to update `auth_token` automatically, number of retries: %d",
                    retries + 1,
                )
                self._update_auth_token()

                return self.__upload(image, retries + 1)
            else:
                return UploadErrorResponse(
                    resp.status_code, resp.json()["error"]["message"], str(image)
                )

    def upload_image(self, image_path: ImagePath) -> Union[str, UploadErrorResponse]:
        logger.debug("uploading: %s", image_path)

        image_path = self._add_watermark(image_path)

        if self.auto_compress:
            # 输入的是路径，返回的也必然是路径，忽略 pyright 的错误提示
            image_path = self._compress_image(image_path)  # type: ignore

        return self.__upload(image_path)

    def upload_image_stream(
        self, image: ImageStream
    ) -> Union[str, UploadErrorResponse]:
        logger.debug("uploading: %s", image.filename)

        if self.auto_compress:
            new_image = self._compress_image(image)
        else:
            new_image = image

        return self.__upload(new_image)

    def upload_images(
        self, *images: ImageType, to_console=True
    ) -> List[Union[str, UploadErrorResponse]]:
        self.check_login()

        check_image_exists(*images)

        self._check_images_valid(*images)

        image_urls: List[Union[str, UploadErrorResponse]] = []
        for img in images:
            if isinstance(img, str):
                result = self.upload_image(img)
            else:
                result = self.upload_image_stream(img)

            image_urls.append(result)

        if to_console:
            for i in image_urls:
                print(i)

        self._clear_cache()
        return image_urls

    def get_all_images(self):
        self.check_login()

        url = self._url(self.username)

        # 集合去重
        images = set()

        def visit_next_page(url):
            resp = requests.get(url, headers=self.__headers, timeout=self.timeout)
            resp.encoding = "utf-8"

            if resp.status_code != 200:
                return ErrorResponse(resp.status_code, resp.text)

            # 只获取默认的公开相册里的图片
            # images_object = re.findall(
            #     r"data-privacy=\"public\" data-object='(.+?)'", resp.text)
            # 获取用户所有图片
            images_object = re.findall(r"data-object='(.+?)'", resp.text)
            images_object = [json.loads(parse.unquote(i)) for i in images_object]
            for image in images_object:
                images.add(
                    (
                        image["url"],
                        image["display_url"],
                        image["id_encoded"],
                        image["width"],
                        image["height"],
                    )
                )

            next_page_url = re.search(
                r'data-pagination="next" href="(.+?)" ><span', resp.text
            )
            if next_page_url:
                next_page_url = next_page_url.group(1)
            else:
                next_page_url = ""

            if next_page_url:
                visit_next_page(next_page_url)

        resp = visit_next_page(url)
        if resp:
            return resp

        result: List[ImgtuResponse] = []

        for item in images:
            result.append(
                ImgtuResponse(
                    item[2],
                    item[0],
                    item[1],
                    int(item[3]),
                    int(item[4]),
                )
            )

        return result

    def delete_image(self, img_id: str, retries=0) -> Optional[ErrorResponse]:
        self.check_login()

        url = self._url("json")
        data = {
            "auth_token": self.token,
            "action": "delete",
            "single": "true",
            "delete": "image",
            "deleting[id]": img_id,
        }
        resp = requests.post(
            url, headers=self.__headers, data=data, timeout=self.timeout
        )
        if resp.status_code == 400:
            if resp.json()["error"]["message"] == "请求被拒绝 (auth_token)":
                if retries >= 3:
                    return ErrorResponse(
                        resp.status_code, resp.json()["error"]["message"]
                    )

                logger.warn(
                    "`auth_token` has expired, the program will try to update `auth_token` automatically, number of retries: %d",
                    retries + 1,
                )
                self._update_auth_token()
                return self.delete_image(img_id, retries + 1)

        if resp.status_code == 200:
            return None

        return ErrorResponse(resp.status_code, resp.json()["error"]["message"])

    def delete_images(self, imgs_id: List[str], retries=0) -> Dict[str, ErrorResponse]:
        self.check_login()

        url = self._url("json")
        data = {
            "auth_token": self.token,
            "action": "delete",
            "from": "list",
            "multiple": "true",
            "delete": "images",
            "deleting[ids][]": imgs_id,
        }
        resp = requests.post(
            url, headers=self.__headers, data=data, timeout=self.timeout
        )
        json_resp = resp.json()
        if resp.status_code == 400:
            if json_resp["error"]["message"] == "请求被拒绝 (auth_token)":
                if retries >= 3:
                    # 删除多张图片时如果重试3次仍无法成功响应则退出程序
                    logger.fatal(
                        "authentication information is invalid: %s",
                        resp.json()["error"]["message"],
                    )

                logger.warn(
                    "`auth_token` has expired, the program will try to update `auth_token` automatically, number of retries: %d",
                    retries + 1,
                )
                self._update_auth_token()
                return self.delete_images(imgs_id, retries + 1)
            elif json_resp["error"]["code"] == 106:
                # imgtu 只有删除的所有 id 都无效时才会返回这个错误
                # 只要有一个有效 id，就会返回 200
                return {img_id: ErrorResponse(404, "服务器中无此图片") for img_id in imgs_id}

        return {}

    def _url(self, path: str) -> str:
        return self.base_url + path

    def __repr__(self):
        return "imgtu.com"
