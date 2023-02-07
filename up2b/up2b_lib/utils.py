#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author:    thepoy
# @Email:     thepoy@163.com
# @File Name: utils.py
# @Created:   2021-02-09 15:17:32
# @Modified:  2023-01-10 13:50:57

import json
import os
import locale
import requests

from functools import wraps, partial
from pathlib import Path
from colorful_logger import get_logger, child_logger as cl
from colorful_logger.logger import is_debug
from urllib.parse import urlparse
from up2b.up2b_lib.constants import (
    CONF_FILE,
    CONFIG_FOLDER_PATH,
    DEFAULT_TIMEOUT,
    IS_MACOS,
    PYTHON_VERSION,
    CACHE_PATH,
)
from up2b.up2b_lib.custom_types import ImageType, ConfigFile, ErrorResponse

log_file_path = None
print_position = False
show = True

if is_debug():
    log_file_path = os.path.join(CONFIG_FOLDER_PATH, "up2b.log")
    print_position = True
    show = True

logger = get_logger(
    "up2b",
    show=show,
    file_path=log_file_path,
    print_position=print_position,
)


def timeout() -> float:
    t = os.getenv("UP2B_TIMEOUT")
    if not t:
        return DEFAULT_TIMEOUT

    try:
        return float(t)
    except ValueError:
        return DEFAULT_TIMEOUT


def child_logger(name: str):
    return cl(name, logger)


def check_image_exists(*images: ImageType):
    for image in images:
        if isinstance(image, str) and not os.path.exists(image):
            raise FileNotFoundError(image)


def read_conf() -> ConfigFile:
    try:
        with open(CONF_FILE) as f:
            conf = json.loads(f.read())

            return conf
    except FileNotFoundError:
        logger.fatal(
            "the configuration file is not found, "
            + "you need to use `--choose-site` or `-c` to select the image bed first."
        )


class Login:
    def __init__(self, func):
        wraps(func)(self)

    def __call__(self, instance, *args, **kwargs):
        return self.__wrapped__(instance, *args, **kwargs)  # type: ignore

    def __get__(self, instance, cls):
        if not instance:
            return partial(self, instance)

        if not instance.auth_info:
            logger.fatal(
                "you have not logged in yet, please use the `-l` or `--login` parameter to log in"
                + " first.\nCurrent image bed code is : `%s`.",
                instance.image_bed_code,
            )

        return partial(self, instance)


def is_ascii(char: str):
    assert len(char) == 1, "只能处理字符，而不是字符串"
    return ord(char) < 128


def get_default_language() -> str:
    if IS_MACOS and PYTHON_VERSION < (3, 7, 5):
        logger.warning(
            f"the version [ {PYTHON_VERSION} ] below 3.7.5 on the macOS platform cannot obtain the system locale, and [ en_US ] is used by default."
        )
        lang = None
    else:
        sys_locale = locale.getdefaultlocale()

        logger.debug(f"system locale: {sys_locale}")

        lang = sys_locale[0]

    return lang if lang else "en_US"


def is_url(path: str) -> bool:
    if not path.startswith("http"):
        return False

    try:
        urlparse(path)
        return True
    except ValueError:
        return False


def download_online_image(url: str):
    logger.debug("下载在线图片：%s", url)

    resp = requests.get(url)
    if resp.status_code != 200:
        logger.error("在线图片下载失败，状态码：%d，响应体：%s", resp.status_code, resp.text)
        return ErrorResponse(resp.status_code, resp.text)

    filename = os.path.basename(url)

    cache_path = CACHE_PATH / filename

    with cache_path.open("wb") as fb:
        fb.write(resp.content)

    logger.debug("在线图片已保存到缓存目录：%s", cache_path)

    return cache_path


def check_path(path: str):
    if not is_url(path):
        logger.debug("'%s' 不是在线图片", path)
        return Path(path)

    logger.info("'%s' 是在线图片", path)

    return download_online_image(path)
