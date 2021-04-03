#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: thepoy
# @Email: thepoy@aliyun.com
# @File Name: sm.py
# @Created: 2021-02-13 09:04:07
# @Modified: 2021-04-03 10:23:38

import requests

from typing import List, Optional, Dict, Any

from up2b.up2b_lib.up2b_api import Base
from up2b.up2b_lib.utils import Login, check_image_exists
from up2b.up2b_lib import errors
from up2b.up2b_lib.constants import SM_MS
from up2b.up2b_lib.custom_types import DeletedResponse


class SM(Base):
    def __init__(self,
                 conf_file: Optional[str] = None,
                 auto_compress: bool = False):
        if not conf_file:
            super().__init__(SM_MS)
        else:
            super().__init__(SM_MS, conf_file)
        self.base_url = "https://sm.ms/api/v2/"
        self.max_size = 5 * 1024 * 1024
        self.auto_compress: bool = auto_compress

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

    def _get_user_profile(self) -> Dict[str, str]:
        url = self._url("profile")
        resp = requests.post(url, headers=self.headers).json()
        if resp["success"]:
            return resp["data"]
        else:
            if self._login_expired(resp):
                self._auto_login()
                self.token = self.auth_info["token"]

    @Login
    def upload_image(self, image_path: str):
        # sm.ms不管出不出错，返回的状态码都是200
        url = self._url("upload")
        headers = {"Authorization": self.token}
        files = {"smfile": open(image_path, "rb")}
        resp = requests.post(url, headers=headers, files=files).json()
        if resp["success"]:
            return resp["data"]["url"]
        else:
            if resp["code"] == "image_repeated":
                # 如果图片重复，会返回重复的图片的链接，所以此处不报错
                return resp["images"]
            elif self._login_expired(resp):
                self._auto_login()
                self.token = self.auth_info["token"]
            else:
                raise errors.UploadFailed(resp["message"])

    @Login
    def upload_images(self, images_path: List[str]) -> List[str]:
        if len(images_path) > 10:
            raise errors.OverSizeError(
                "You can only upload up to 10 pictures, but you uploaded %d pictures."
                % len(images_path))

        check_image_exists(images_path)

        self._check_images_valid(images_path)

        images_url = []
        for img in images_path:
            try:
                result = self.upload_image(img)
            except errors.UploadFailed as e:
                result = {
                    "image_path": img,
                    "status_code": 400,
                    "error": f"{e}",
                }

            images_url.append(result)

        for i in images_url:
            print(i)

        self._clear_cache()

        return images_url

    @Login
    def history(self) -> Dict[str, Any]:
        """
        Temporary History - IP Based Temporary Upload History
        """
        url = self._url("history")
        resp = requests.get(url, headers=self.headers)
        return resp.json()

    @Login
    def clear(self) -> Dict[str, Any]:
        """
        Clear Temporary History - Clear IP Based Temporary Upload History
        """
        url = self._url("clear")
        resp = requests.get(url, headers=self.headers)
        return resp.json()

    @Login
    def upload_history(self) -> dict:
        url = self._url("upload_history")
        resp = requests.get(url, headers=self.headers)
        return resp.json()

    @Login
    def get_all_images(self) -> List[Dict[str, str]]:
        images = []
        for file in self.upload_history()["data"]:
            images.append({
                "url": file["url"],
                "delete_url": file["delete"],
                "width": file["width"],
                "height": file["height"],
            })

        return images

    @Login
    def delete_image(self, delete_url: str) -> DeletedResponse:
        resp = requests.get(delete_url, headers=self.headers)
        # TODO: sm.ms 删除图片后本应返回json，但实际返回的是html。而且删除链接不需要认证，任何人get都能删除图片
        return resp.status_code == 200

    @Login
    def delete_images(self, urls: List[str]) -> dict:
        result = {}
        for url in urls:
            r = self.delete_image(url)
            # if not r["success"]:
            #     result[hash] = {"message": r["message"], "code": r["code"]}
            result[url] = r
        return result

    @Login
    def get_all_images_in_image_bed(self) -> List[str]:
        pass

    def _url(self, path: str) -> str:
        return self.base_url + path

    def _login_expired(self, resp: dict):
        return resp[
            "message"] == "Get user profile failed, invalid Authorization."

    def __str__(self):
        return "sm.ms"
