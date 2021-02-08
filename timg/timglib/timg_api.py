#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: thepoy
# @Email: thepoy@aliyun.com
# @File Name: timg_api.py
# @Created: 2021-02-08 09:11:21
# @Modified: 2021-02-08 21:43:02

import os
import sys
import json
import requests

from typing import Optional, List

from timg.timglib import errors

IS_WINDOWS = sys.platform == "win32"

if not IS_WINDOWS:
    HOME = os.environ["HOME"]


class Base:
    def __init__(self):
        self.tokens_file: str = os.path.join(
            HOME,
            ".config",
            "Typora",
            "conf",
            "timg.user_tokens.json",
        )
        self.token: Optional[str] = self._read_token()
        self.key: Optional[str] = None

    def _read_token(self) -> Optional[str]:
        try:
            with open(self.tokens_file) as f:
                tokens = json.loads(f.read())
                return tokens[self.key]
        except Exception:
            return ""

    def _save_token(self, token: str):
        try:
            with open(self.tokens_file, "r+") as f:
                tokens = json.loads(f.read())
                tokens[self.key] = token
                f.seek(0)
                f.write(json.dumps(tokens))
        except FileNotFoundError:
            with open(self.tokens_file, "w") as f:
                f.write(json.dumps({self.key: token}))
        except Exception as e:
            print(e)


class SM(Base):
    def __init__(self):
        super().__init__()
        self.key = "sm"
        self.base_url = "https://sm.ms/api/v2/"

        self._read_token()

        self.headers = {
            "Content-Type": "multipart/form-data",
            "Authorization": self.token
        }

    def login(self, username: str, password: str):
        token = self._get_api_token(username, password)
        self._save_token(token)

    def _get_api_token(self, username: str, password: str) -> str:
        url = self._url("token")
        data = {"username": username, "password": password}
        resp = requests.post(url, data=data).json()
        return resp["data"]["token"]

    def _get_user_profile(self):
        url = self._url("profile")
        resp = requests.post(url, headers=self.headers).json()
        if resp["success"]:
            print(resp["data"])
        else:
            if self._login_expired(resp):
                self.login()

    def upload_image(self, image_path: str):
        url = self._url("upload")
        headers = {"Authorization": self.token}
        files = {"smfile": open(image_path, "rb")}
        resp = requests.post(url, headers=headers, files=files).json()
        if resp["success"]:
            return resp["data"]["url"]
        else:
            # print(resp)
            if resp["code"] == "image_repeated":
                return resp["images"]
            else:
                raise errors.UploadFailed(resp["message"])

    def upload_images(self, images_path: List[str]):
        if len(images_path) > 10:
            raise errors.OverLimitError(
                "You can only upload up to 10 pictures, but you uploaded %d pictures."
                % len(images_path))

        for img in images_path:
            if not os.path.exists(img):
                raise FileNotFoundError(img)

        url = self._url("upload")
        headers = {"Authorization": self.token}

        images_url = []
        for img in images_path:
            files = {"smfile": open(img, "rb")}
            resp = requests.post(url, headers=headers, files=files).json()
            if resp["success"]:
                images_url.append(resp["data"]["url"])
            else:
                if resp["code"] == "image_repeated":
                    images_url.append(resp["images"])

        for i in images_url:
            print(i)

    def _url(self, key: str) -> str:
        return self.base_url + key

    def _login_expired(self, resp: dict):
        return resp[
            "message"] == "Get user profile failed, invalid Authorization."
