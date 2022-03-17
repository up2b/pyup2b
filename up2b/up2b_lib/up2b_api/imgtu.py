#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: thepoy
# @Email: thepoy@aliyun.com
# @File Name: imgtu.py
# @Created: 2021-02-13 09:04:37
# @Modified:  2022-03-17 19:48:21

import os
import re
import time
import json
import mimetypes
import requests

from urllib import parse
from typing import List, Optional, Tuple, Union

from requests_toolbelt import MultipartEncoder

from up2b.up2b_lib.custom_types import ImageType, ImageStream, ImagePath
from up2b.up2b_lib.up2b_api import Base, ImageBedMixin, CONF_FILE
from up2b.up2b_lib.utils import Login, check_image_exists, child_logger
from up2b.up2b_lib.constants import IMGTU

logger = child_logger(__name__)


class Imgtu(Base, ImageBedMixin):
    def __init__(
        self,
        auto_compress: bool = False,
        add_watermark: bool = False,
        conf_file: str = CONF_FILE,
    ):
        self.image_bed_code = IMGTU
        super().__init__(auto_compress, add_watermark, conf_file)

        self.base_url: str = "https://imgtu.com/"
        self.max_size = 10 * 1024 * 1024

        self.headers = {
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:85.0) Gecko/20100101 Firefox/85.0",
        }

        self.cookie: Optional[str] = None
        self.token: Optional[str] = None
        if self.auth_info:
            self.cookie = self.auth_info["cookie"]
            self.token = self.auth_info["token"]
            self.username = self.auth_info["username"]
            self.headers["Cookie"] = self.cookie

    def login(self, username: str, password: str) -> bool:
        url = self._url("login")
        auth_token, cookie = self._parse_auth_token()

        if not auth_token or not cookie:
            raise Exception("auth token or cookie is None")

        headers = self.headers.copy()
        headers["Cookie"] = cookie

        data = {
            "login-subject": username,
            "password": password,
            "auth_token": auth_token,
        }

        resp = requests.post(url, headers=headers, data=data, allow_redirects=False)
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
        resp = requests.get(url, headers=self.headers)
        if resp.status_code == 200:
            auth_token = re.search(
                r'PF.obj.config.auth_token = "([a-f0-9]{40})"', resp.text
            )
            if not auth_token:
                return None, None
            resp_set_cookie = resp.headers["Set-Cookie"].split("; ")[0]
            return auth_token.group(1), resp_set_cookie
        else:
            logger.error("响应错误: %d", resp.status_code)
            return None, None

    def _update_auth_token(self):
        headers = {
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:85.0) Gecko/20100101 Firefox/85.0",
            "Cookie": self.cookie,
        }
        resp = requests.get(self.base_url, headers=headers)
        auth_token = re.search(
            r'PF.obj.config.auth_token = "([a-f0-9]{40})"', resp.text
        )
        if auth_token:
            auth_token = auth_token.group(1)
            if not self.auth_info:
                self.auth_info = {}

            self.auth_info["token"] = self.token = auth_token
            self._save_auth_info(self.auth_info)

    def __upload(self, image: ImageType):
        is_path = isinstance(image, str)

        url = self._url("json")
        headers = {
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:85.0) Gecko/20100101 Firefox/85.0",
            "Cookie": self.cookie,
        }

        filename_with_suffix = os.path.basename(image if is_path else image.filename)
        filename_without_suffix, suffix = os.path.splitext(filename_with_suffix)
        if is_path:
            if suffix.lower() == ".apng":
                suffix = ".png"
            filename = filename_without_suffix + suffix
        else:
            filename = filename_with_suffix + "." + image.mime_type

        mime_type = mimetypes.guess_type(image)[0] if is_path else image.mime_type

        timestamp = int(time.time() * 1000)

        if is_path:
            with open(image, "rb") as fb:
                img_buffer = fb.read()
        else:
            img_buffer = image.stream

        data = MultipartEncoder(
            {
                "source": (filename, img_buffer, mime_type),
                "type": "file",
                "action": "upload",
                "timestamp": str(timestamp),
                "auth_token": self.token,
                "nsfw": "0",
            }
        )
        headers.update({"Content-Type": data.content_type})
        resp = requests.post(url, headers=headers, data=data)  # type: ignore
        resp.encoding = "utf-8"
        try:
            uploaded_url = resp.json()["image"]["image"]["url"]
            logger.debug(
                "uploaded url: %s => %s",
                image if is_path else image.filename,
                uploaded_url,
            )

            return uploaded_url
        except KeyError:
            if resp.json()["error"]["message"] == "请求被拒绝 (auth_token)":
                logger.warn(
                    "`auth_token` has expired, the program will try to update `auth_token` automatically."
                )
                self._update_auth_token()
                return self.upload_image(image)
            else:
                resp = resp.json()
                logger.error(
                    "upload failed: img=%s, error=%s",
                    image if is_path else image.filename,
                    resp["error"]["message"],
                )
                return resp
        except json.decoder.JSONDecodeError:
            logger.fatal(resp.text)

    @Login
    def upload_image(self, image_path: ImagePath) -> Union[str, dict]:  # type: ignore
        logger.debug("uploading: %s", image_path)

        image_path = self._add_watermark(image_path)

        if self.auto_compress:
            # 输入的是路径，返回的也必然是路径，忽略 pyright 的错误提示
            image_path = self._compress_image(image_path)  # type: ignore

        return self.__upload(image_path)

    @Login
    def upload_image_stream(self, image: ImageStream) -> str:
        logger.debug("uploading: %s", image.filename)

        if self.auto_compress:
            new_image = self._compress_image(image)
        else:
            new_image = image

        return self.__upload(new_image)

    @Login
    def upload_images(self, *images_path: ImageType, to_console=True) -> list:
        check_image_exists(*images_path)

        self._check_images_valid(images_path)

        images_url = []
        for img in images_path:
            if isinstance(img, str):
                result = self.upload_image(img)
            else:
                result = self.upload_image_stream(img)

            if type(result) == str:
                images_url.append(result)
            elif type(result) == dict:
                images_url.append(
                    {
                        "image_path": img,
                        "status_code": result["status_code"],
                        "error": result["error"]["message"],
                    }
                )

        if to_console:
            for i in images_url:
                print(i)

        self._clear_cache()
        return images_url

    @Login
    def get_all_images(self):
        url = self._url(self.username)

        # 集合去重
        images = set()

        def visit_next_page(url):
            resp = requests.get(url, headers=self.headers)
            resp.encoding = "utf-8"

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
                # images.append({
                #     "url": image["url"],
                #     "display_url": image["display_url"],
                #     "id": image["id_encoded"],
                #     "width": image["width"],
                #     "height": image["height"],
                # })

            next_page_url = re.search(
                r'data-pagination="next" href="(.+?)" ><span', resp.text
            )
            if next_page_url:
                next_page_url = next_page_url.group(1)
            else:
                next_page_url = ""

            if next_page_url:
                visit_next_page(next_page_url)

        visit_next_page(url)

        result = []

        for item in images:
            result.append(
                {
                    "url": item[0],
                    "display_url": item[1],
                    "id": item[2],
                    "width": item[3],
                    "height": item[4],
                }
            )

        return result

    @Login
    def delete_image(self, img_id: str):
        url = self._url("json")
        data = {
            "auth_token": self.token,
            "action": "delete",
            "single": "true",
            "delete": "image",
            "deleting[id]": img_id,
        }
        resp = requests.post(url, headers=self.headers, data=data)
        if resp.status_code == 400:
            if resp.json()["error"]["message"] == "请求被拒绝 (auth_token)":
                logger.warn(
                    "`auth_token` has expired, the program will try to update `auth_token` automatically."
                )
                self._update_auth_token()
                return self.delete_image(img_id)
        return resp.json()

    @Login
    def delete_images(self, imgs_id: List[str]):
        url = self._url("json")
        data = {
            "auth_token": self.token,
            "action": "delete",
            "from": "list",
            "multiple": "true",
            "delete": "images",
            "deleting[ids][]": imgs_id,
        }
        resp = requests.post(url, headers=self.headers, data=data)
        if resp.status_code == 400:
            if resp.json()["error"]["message"] == "请求被拒绝 (auth_token)":
                logger.warn(
                    "`auth_token` has expired, the program will try to update `auth_token` automatically."
                )
                self._update_auth_token()
                return self.delete_images(imgs_id)
        return resp.json()

    def _url(self, path: str) -> str:
        return self.base_url + path

    def __repr__(self):
        return "imgtu.com"
