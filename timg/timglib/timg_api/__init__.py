#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: thepoy
# @Email: thepoy@aliyun.com
# @File Name: __init__.py
# @Created: 2021-02-13 09:02:21
# @Modified: 2021-02-13 10:44:08

import os
import sys
import json

from typing import Optional, List, Tuple, Dict

from timg.timglib import custom_types
from timg.timglib.utils import Login

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


def choose_image_bed(key: str, conf_file: str = CONF_FILE):
    try:
        with open(conf_file, "r+") as f:
            conf = json.loads(f.read())
            f.seek(0, 0)
            conf["image_bed"] = key
            f.write(json.dumps(conf))
            f.truncate()
    except FileNotFoundError:
        with open(conf_file, "w") as f:
            f.write(json.dumps({"image_bed": key}))


class Base:
    def __init__(self, key: str, conf_file: str = CONF_FILE):
        self.conf_file: str = conf_file
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
            with open(self.conf_file) as f:
                conf = json.loads(f.read())
                return conf["auth_data"][self.key]
        except Exception:
            return None

    def _save_auth_info(self, auth_info: Dict[str, str]):
        try:
            with open(self.conf_file, "r+") as f:
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
                "Error: Auth configure file is not found, "
                "please choose image bed with `--choose-site` or `-c` first.")
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