#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: thepoy
# @Email: thepoy@aliyun.com
# @File Name: sm.py
# @Created: 2021-02-13 09:04:07
# @Modified: 2021-02-13 09:30:15

import requests

from typing import List, Optional

from timg.timglib.timg_api import Base
from timg.timglib.utils import Login, check_image_exists
from timg.timglib import errors
from timg.timglib.constants import SM_MS


class SM(Base):
    def __init__(self, conf_file: Optional[str] = None):
        if not conf_file:
            super().__init__(SM_MS)
        else:
            super().__init__(SM_MS, conf_file)
        self.base_url = "https://sm.ms/api/v2/"
        self.max_size = 5

        if self.auth_info:
            self.token: str = self.auth_info["token"]

            self.headers = {
                "Content-Type": "multipart/form-data",
                "Authorization": self.token
            }

    def login(self, username: str, password: str):
        token = self._get_api_token(username, password)
        self._save_auth_info({
            "token": token,
            "username": username,
            "password": password
        })

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
                self._auto_login()
                self.token = self.auth_info["token"]

    @Login
    def upload_image(self, image_path: str):
        url = self._url("upload")
        headers = {"Authorization": self.token}
        files = {"smfile": open(image_path, "rb")}
        resp = requests.post(url, headers=headers, files=files).json()
        if resp["success"]:
            return resp["data"]["url"]
        else:
            if resp["code"] == "image_repeated":
                return resp["images"]
            elif self._login_expired(resp):
                self._auto_login()
                self.token = self.auth_info["token"]
            else:
                raise errors.UploadFailed(resp["message"])

    @Login
    def upload_images(self, images_path: List[str]):
        if len(images_path) > 10:
            raise errors.OverLimitError(
                "You can only upload up to 10 pictures, but you uploaded %d pictures."
                % len(images_path))

        check_image_exists(images_path)

        exceeded, _img = self._exceed_max_size(*images_path)
        if exceeded:
            raise errors.OverSizeError(_img)

        images_url = []
        for img in images_path:
            images_url.append(self.upload_image(img))

        for i in images_url:
            print(i)

    @Login
    def delete_image(self, *args):
        pass

    @Login
    def delete_images(self, *args):
        pass

    def _url(self, key: str) -> str:
        return self.base_url + key

    def _login_expired(self, resp: dict):
        return resp[
            "message"] == "Get user profile failed, invalid Authorization."
