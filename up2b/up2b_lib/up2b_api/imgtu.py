#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: thepoy
# @Email: thepoy@aliyun.com
# @File Name: imgtu.py
# @Created: 2021-02-13 09:04:37
# @Modified: 2021-04-03 10:21:15

import sys
import os
import re
import time
import json
import mimetypes
import requests

from urllib import parse
from typing import List, Optional, Tuple, Union

from requests_toolbelt import MultipartEncoder

from up2b.up2b_lib.up2b_api import Base
from up2b.up2b_lib.utils import Login, check_image_exists
from up2b.up2b_lib.constants import IMGTU


class Imgtu(Base):
    def __init__(self,
                 conf_file: Optional[str] = None,
                 auto_compress: bool = False):
        if not conf_file:
            super().__init__(IMGTU)
        else:
            super().__init__(IMGTU, conf_file)
        self.base_url: str = "https://imgtu.com/"
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
            self.username = self.auth_info["username"]
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
        resp = requests.get(self.base_url, headers=headers)
        auth_token = re.search(r'PF.obj.config.auth_token = "([a-f0-9]{40})"',
                               resp.text).group(1)
        self.auth_info["token"] = self.token = auth_token
        self._save_auth_info(self.auth_info)

    @Login
    def upload_image(self, image_path: str) -> Union[str, dict]:
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
                return resp.json()

    @Login
    def upload_images(self, images_path: List[str]) -> list:
        check_image_exists(images_path)

        self._check_images_valid(images_path)

        images_url = []
        for img in images_path:
            result = self.upload_image(img)
            if type(result) == str:
                images_url.append(result)
            elif type(result) == dict:
                images_url.append({
                    "image_path": img,
                    "status_code": result["status_code"],
                    "error": result["error"]["message"],
                })

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
            images_object = [
                json.loads(parse.unquote(i)) for i in images_object
            ]
            for image in images_object:
                images.add((
                    image["url"],
                    image["display_url"],
                    image["id_encoded"],
                    image["width"],
                    image["height"],
                ))
                # images.append({
                #     "url": image["url"],
                #     "display_url": image["display_url"],
                #     "id": image["id_encoded"],
                #     "width": image["width"],
                #     "height": image["height"],
                # })

            next_page_url = re.search(
                r'data-pagination="next" href="(.+?)" ><span', resp.text)
            if next_page_url:
                next_page_url = next_page_url.group(1)
            else:
                next_page_url = ""

            if next_page_url:
                visit_next_page(next_page_url)

        visit_next_page(url)

        result = []

        for item in images:
            result.append({
                "url": item[0],
                "display_url": item[1],
                "id": item[2],
                "width": item[3],
                "height": item[4],
            })

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

    def _url(self, path: str) -> str:
        return self.base_url + path

    def __str__(self):
        return "imgtu.com"
