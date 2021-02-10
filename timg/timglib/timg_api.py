#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: thepoy
# @Email: thepoy@aliyun.com
# @File Name: timg_api.py
# @Created: 2021-02-08 09:11:21
# @Modified: 2021-02-10 14:45:57

import os
import re
import sys
import json
import time
import mimetypes

import requests

from typing import Optional, List, Tuple, Dict

from requests_toolbelt import MultipartEncoder

from timg.timglib import errors
from timg.timglib import custom_types
from timg.timglib.utils import Login, check_image_exists

IS_WINDOWS = sys.platform == "win32"

if not IS_WINDOWS:
    CONF_FILE = os.path.join(
        os.environ["HOME"],
        ".config",
        "Typora",
        "conf",
        "conf.timg.json",
    )
else:
    CONF_FILE = os.path.join(
        os.environ['APPDATA'],
        "Typora",
        "conf",
        "conf.timg.json",
    )


def choose_image_bed(key: str):
    try:
        with open(CONF_FILE, "r+") as f:
            conf = json.loads(f.read())
            f.seek(0, 0)
            conf["image_bed"] = key
            f.write(json.dumps(conf))
            f.truncate()
    except FileNotFoundError:
        with open(CONF_FILE, "w") as f:
            f.write(json.dumps({"image_bed": key}))


class Base:
    def __init__(self, key: str):
        self.max_size: int = 0
        self.key: Optional[str] = key
        self.auth_info: Optional[
            custom_types.AuthInfo] = self._read_auth_info()

    def login(self, username: str, password: str):
        pass

    @Login
    def upload_image(self, image_path: str) -> str:
        pass

    @Login
    def upload_images(self, images_path: List[str]):
        pass

    def _read_auth_info(self) -> Optional[custom_types.AuthInfo]:
        try:
            with open(CONF_FILE) as f:
                conf = json.loads(f.read())
                return conf["auth_data"][self.key]
        except Exception:
            return None

    def _save_auth_info(self, auth_info: Dict[str, str]):
        try:
            with open(CONF_FILE, "r+") as f:
                conf = json.loads(f.read())
                try:
                    conf['auth_data'][self.key] = auth_info
                except KeyError:
                    conf["auth_data"] = {}
                    conf['auth_data'][self.key] = auth_info
                f.seek(0, 0)
                f.write(json.dumps(conf))
                f.truncate()
        except FileNotFoundError:
            print(
                "Error: Auth configure file is not found, please choose image bed with `--choose-site` or `-c` first."
            )
            sys.exit(0)
        except Exception as e:
            print(e)

    def _auto_login(self):
        username = self.auth_info["username"]
        password = self.auth_info["password"]
        self.login(username, password)
        self.auth_info = self._read_auth_info()

    def _exceed_max_size(self,
                         *images_path: str) -> Tuple[bool, Optional[str]]:
        for img in images_path:
            if os.path.getsize(img) / 1024 / 1024 > self.max_size:
                return True, img
        return False, None


class SM(Base):
    def __init__(self):
        super().__init__("sm")
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


class Chr(Base):
    def __init__(self):
        super().__init__("chr")

        self.max_size = 10

        self.headers = {
            "User-Agent":
            "Mozilla/5.0 (X11; Linux x86_64; rv:85.0) Gecko/20100101 Firefox/85.0"
        }

        self.cookie: Optional[str] = None
        self.token: Optional[str] = None
        if self.auth_info:
            self.cookie = self.auth_info["cookie"]
            self.token = self.auth_info["token"]

    def login(self, username: str, password: str):
        url = "https://imgchr.com/login"
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
            self.cookie = cookie + "; " + resp.headers["Set-Cookie"].split(
                "; ")[0]
            auth_info = {
                "token": auth_token,
                "cookie": self.cookie,
                "username": username,
                "password": password
            }
            self._save_auth_info(auth_info)
        else:
            print("Error: Login failed.")
            sys.exit(0)

    def _parse_auth_token(self) -> Tuple[Optional[str], Optional[str]]:
        url = "https://imgchr.com/login"
        resp = requests.get(url, headers=self.headers)
        if resp.status_code == 200:
            auth_token = re.search(
                r'PF.obj.config.auth_token = "([a-f0-9]{40})"', resp.text)
            resp_set_cookie = resp.headers["Set-Cookie"].split("; ")[0]
            return auth_token.group(1), resp_set_cookie
        else:
            print("响应错误:", resp.status_code)
            return None, None

    @Login
    def upload_image(self, image_path: str) -> str:
        url = "https://imgchr.com/json"
        headers = {
            "Accept": "application/json",
            "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36 Edg/88.0.705.63",
            "Cookie": self.cookie,
        }

        filename = os.path.basename(image_path)

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
                print(resp.json())
                print(
                    "Warning: Login has expired, the program will try to log in automatically."
                )
                self._auto_login()
                self.cookie = self.auth_info["cookie"]
                self.token = self.auth_info["token"]
                return self.upload_image(image_path)
            else:
                print(resp.json())

    @Login
    def upload_images(self, images_path: List[str]):
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
