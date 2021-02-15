#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: thepoy
# @Email: thepoy@aliyun.com
# @File Name: chr.py
# @Created: 2021-02-13 09:04:37
# @Modified: 2021-02-15 19:06:33

import sys
import os
import re
import time
import mimetypes
import requests

from typing import List, Optional, Tuple

from requests_toolbelt import MultipartEncoder

from timg.timglib.timg_api import Base
from timg.timglib.utils import Login, check_image_exists
from timg.timglib.constants import IMAGE_CHR


class Chr(Base):
    def __init__(self,
                 conf_file: Optional[str] = None,
                 auto_compress: bool = False):
        if not conf_file:
            super().__init__(IMAGE_CHR)
        else:
            super().__init__(IMAGE_CHR, conf_file)
        self.base_url: str = "https://imgchr.com/"
        self.max_size = 10 * 1024 * 1024
        self.auto_compress: bool = auto_compress

        self.headers = {
            "Accept":
            "application/json",
            "User-Agent":
            "Mozilla/5.0 (X11; Linux x86_64; rv:85.0) Gecko/20100101 Firefox/85.0"
        }

        self.cookie: Optional[str] = None
        self.token: Optional[str] = None
        if self.auth_info:
            self.cookie = self.auth_info["cookie"]
            self.token = self.auth_info["token"]
            self.headers["Cookie"] = self.cookie

    def login(self, username: str, password: str):
        url = self._url("login")
        auth_token, cookie = self._parse_auth_token()

        headers = self.headers.copy()
        headers["Cookie"] = cookie

        data = {
            "login-subject": username,
            "password": password,
            "auth_token": auth_token,
        }

        resp = requests.post(url,
                             headers=headers,
                             data=data,
                             allow_redirects=False)
        if resp.status_code == 301:
            # If there is a KEEPLOGIN field in the cookie,
            # pictures will be uploaded as a normal user
            self.cookie = cookie + "; " + resp.headers["Set-Cookie"].split(
                "; ")[0]

            # If there is no KEEPLOGIN field in the cookie,
            # pictures will be uploaded as a tourist
            # self.cookie = cookie

            auth_info = {
                "token": auth_token,
                "cookie": self.cookie,
                "username": username,
                "password": password
            }
            self._save_auth_info(auth_info)
        else:
            print("Error: Login failed.")
            sys.exit(1)

    def _parse_auth_token(self) -> Tuple[Optional[str], Optional[str]]:
        url = self._url("login")
        resp = requests.get(url, headers=self.headers)
        if resp.status_code == 200:
            auth_token = re.search(
                r'PF.obj.config.auth_token = "([a-f0-9]{40})"', resp.text)
            resp_set_cookie = resp.headers["Set-Cookie"].split("; ")[0]
            return auth_token.group(1), resp_set_cookie
        else:
            print("响应错误:", resp.status_code)
            return None, None

    def _update_auth_token(self):
        headers = {
            "Accept": "application/json",
            "User-Agent":
            "Mozilla/5.0 (X11; Linux x86_64; rv:85.0) Gecko/20100101 Firefox/85.0",
            "Cookie": self.cookie,
        }
        resp = requests.get("https://imgchr.com", headers=headers)
        auth_token = re.search(r'PF.obj.config.auth_token = "([a-f0-9]{40})"',
                               resp.text).group(1)
        self.auth_info["token"] = self.token = auth_token
        self._save_auth_info(self.auth_info)

    @Login
    def upload_image(self, image_path: str) -> str:
        image_path = self._compress_image(image_path)
        url = self._url("json")
        headers = {
            "Accept": "application/json",
            "User-Agent":
            "Mozilla/5.0 (X11; Linux x86_64; rv:85.0) Gecko/20100101 Firefox/85.0",
            "Cookie": self.cookie,
        }

        filename_with_suffix = os.path.basename(image_path)
        filename_without_suffix, suffix = os.path.splitext(
            filename_with_suffix)
        if suffix.lower() == '.apng':
            suffix = ".png"
        filename = filename_without_suffix + suffix

        mime_type = mimetypes.guess_type(image_path)[0]

        timestamp = int(time.time() * 1000)
        data = MultipartEncoder({
            "source": (filename, open(image_path, "rb"), mime_type),
            "type":
            "file",
            "action":
            "upload",
            "timestamp":
            str(timestamp),
            "auth_token":
            self.token,
            "nsfw":
            "0",
        })
        headers.update({"Content-Type": data.content_type})
        resp = requests.post(url, headers=headers, data=data)
        resp.encoding = "utf-8"
        try:
            return resp.json()["image"]["image"]["url"]
        except KeyError:
            if resp.json()["error"]["message"] == '请求被拒绝 (auth_token)':
                print(
                    "Warning: `auth_token` has expired, "
                    "the program will try to update `auth_token` automatically."
                )
                self._update_auth_token()
                return self.upload_image(image_path)
            else:
                print(resp.json())

    @Login
    def upload_images(self, images_path: List[str]):
        check_image_exists(images_path)

        self._check_images_valid(images_path)

        images_url = []
        for img in images_path:
            images_url.append(self.upload_image(img))

        for i in images_url:
            print(i)

        self._clear_cache()

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
            if resp.json()["error"]["message"] == '请求被拒绝 (auth_token)':
                print(
                    "Warning: `auth_token` has expired, "
                    "the program will try to update `auth_token` automatically."
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
            if resp.json()["error"]["message"] == '请求被拒绝 (auth_token)':
                print(
                    "Warning: `auth_token` has expired, "
                    "the program will try to update `auth_token` automatically."
                )
                self._update_auth_token()
                return self.delete_images(imgs_id)
        return resp.json()

    def _url(self, key: str) -> str:
        return self.base_url + key
