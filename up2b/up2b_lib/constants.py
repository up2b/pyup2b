#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author:    thepoy
# @Email:     thepoy@aliyun.com
# @File Name: constants.py
# @Created:   2021-02-13 09:17:07
# @Modified:  2022-03-30 11:11:52

import sys
import os

from enum import IntEnum

PYTHON_VERSION = sys.version_info


class ImageBedCode(IntEnum):
    SM_MS = 0
    IMGTU = 1
    GITHUB = 2


DEFAULT_TIMEOUT = 10.0

# fmt: off
IMAGE_BEDS_CODE = {
    "sm.ms":      ImageBedCode.SM_MS,
    "imgtu.com":  ImageBedCode.IMGTU,
    "github.com": ImageBedCode.GITHUB,
}
# fmt: on


IS_WINDOWS = sys.platform == "win32"
IS_MACOS = sys.platform == "darwin"

if IS_WINDOWS:
    CONFIG_FOLDER_PATH = os.path.join(os.environ["APPDATA"], "up2b")
else:
    CONFIG_FOLDER_PATH = os.path.join(os.environ["HOME"], ".config", "up2b")

if not os.path.exists(CONFIG_FOLDER_PATH):
    os.makedirs(os.path.join(CONFIG_FOLDER_PATH, "conf"), 0o755)

CONF_FILE = os.path.join(CONFIG_FOLDER_PATH, "conf", "conf.up2b.json")
CACHE_PATH = os.path.join(CONFIG_FOLDER_PATH, "cache")
