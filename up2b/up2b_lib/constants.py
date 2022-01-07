#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: thepoy
# @Email: thepoy@aliyun.com
# @File Name: constants.py
# @Created: 2021-02-13 09:17:07
# @Modified: 2021-07-25 23:26:27

import sys
import os

SM_MS = 0
IMGTU = 1
GITEE = 2
GITHUB = 3

# fmt: off
IMAGE_BEDS_CODE = {
    "sm.ms": SM_MS,
    "imgtu.com": IMGTU,
    "gitee.com": GITEE,
    "github.com": GITHUB,
}
# fmt: on


IS_WINDOWS = sys.platform == "win32"
IS_MACOS = sys.platform == "darwin"

if IS_WINDOWS:
    CONFIG_FOLDER_PATH = os.path.join(os.environ["APPDATA"], "up2b")
elif IS_MACOS:
    CONFIG_FOLDER_PATH = os.path.join(os.environ["HOME"], ".config", "up2b")
else:
    CONFIG_FOLDER_PATH = os.path.join(os.environ["HOME"], ".config", "up2b")

if not os.path.exists(CONFIG_FOLDER_PATH):
    os.makedirs(os.path.join(CONFIG_FOLDER_PATH, "conf"), 0o755)

CONF_FILE = os.path.join(CONFIG_FOLDER_PATH, "conf", "conf.up2b.json")
CACHE_PATH = os.path.join(CONFIG_FOLDER_PATH, "cache")
