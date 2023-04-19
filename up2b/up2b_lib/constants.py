#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author:      thepoy
# @Email:       thepoy@163.com
# @File Name:   constants.py
# @Created At:  2021-02-13 09:17:07
# @Modified At: 2023-04-19 14:42:31
# @Modified By: thepoy

import sys
import os

from enum import IntEnum
from pathlib import Path
from tempfile import gettempdir

PYTHON_VERSION = sys.version_info


class ImageBedCode(IntEnum):
    SM_MS = 0
    IMGTU = 1
    GITHUB = 2
    # CODING = 3 # 废弃
    IMGTG = 4

    def __repr__(self) -> str:
        return str(self.value)

    def __str__(self) -> str:
        return str(self.value)


DEFAULT_TIMEOUT = 10.0

# fmt: off
IMAGE_BEDS_CODE = {
    "sm.ms":      ImageBedCode.SM_MS,
    "imgse.com":  ImageBedCode.IMGTU,
    "github.com": ImageBedCode.GITHUB,
    "imgtg.com": ImageBedCode.IMGTG,
}
# fmt: on


IMAGE_BEDS_NAME = {v: k for k, v in IMAGE_BEDS_CODE.items()}

IMAGE_BEDS_HELP_MESSAGE = "\n\n".join([f"{v}: {k}" for k, v in IMAGE_BEDS_CODE.items()])


IS_WINDOWS = sys.platform == "win32"
IS_MACOS = sys.platform == "darwin"

CONFIG_FOLDER_PATH = (
    Path(os.environ["APPDATA"]) / "up2b"
    if IS_WINDOWS
    else Path(os.environ["HOME"]) / ".config" / "up2b"
)

if not CONFIG_FOLDER_PATH.exists():
    os.makedirs(CONFIG_FOLDER_PATH / "conf", 0o755)

CONF_FILE = CONFIG_FOLDER_PATH / "conf" / "conf.up2b.json"
CACHE_PATH = Path(gettempdir()) / "up2b"
CACHE_DATABASE = CONFIG_FOLDER_PATH / "cache.db"
