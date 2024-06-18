#!/usr/bin/env python3
# -*- coding:utf-8 -*-

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
    "imgtg.com":  ImageBedCode.IMGTG,
}
# fmt: on


IMAGE_BEDS_NAME = {v: k for k, v in IMAGE_BEDS_CODE.items()}

IMAGE_BEDS_HELP_MESSAGE = "\n\n".join([f"{v}: {k}" for k, v in IMAGE_BEDS_CODE.items()])


IS_WINDOWS = sys.platform == "win32"
IS_MACOS = sys.platform == "darwin"

UP2B_CONFIG_ROOT_DIR = (
    Path(os.environ["APPDATA"]) / "up2b"
    if IS_WINDOWS
    else Path(os.environ["HOME"]) / ".config" / "up2b"
)

UP2B_CONFIG_DIR = UP2B_CONFIG_ROOT_DIR / "conf"

if not UP2B_CONFIG_ROOT_DIR.exists():
    os.makedirs(UP2B_CONFIG_DIR, 0o755)

CONFIG_FILE = UP2B_CONFIG_DIR / "conf.up2b.json"

if not CONFIG_FILE.parent.exists():
    CONFIG_FILE.parent.mkdir(parents=True)

CACHE_PATH = Path(gettempdir()) / "up2b"
CACHE_DATABASE = UP2B_CONFIG_ROOT_DIR / "cache.db"
