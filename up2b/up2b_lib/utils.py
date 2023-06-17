#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author:      thepoy
# @Email:       thepoy@163.com
# @File Name:   utils.py
# @Created At:  2021-02-09 15:17:32
# @Modified At: 2023-03-09 10:11:26
# @Modified By: thepoy

import json
import os
import locale
import requests

from typing import List, Sequence, Tuple, Union
from functools import wraps, partial
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse
from up2b.up2b_lib.constants import (
    CONF_FILE,
    DEFAULT_TIMEOUT,
    IS_MACOS,
    PYTHON_VERSION,
    CACHE_PATH,
)
from up2b.up2b_lib.custom_types import (
    DownloadErrorResponse,
    ImageType,
    ConfigFile,
)
from up2b.up2b_lib.log import child_logger


logger = child_logger(__name__)


def timeout() -> float:
    t = os.getenv("UP2B_TIMEOUT")
    if not t:
        return DEFAULT_TIMEOUT

    try:
        return float(t)
    except ValueError:
        return DEFAULT_TIMEOUT


def check_image_exists(images: Tuple[Union[ImageType, DownloadErrorResponse]]):
    for image in images:
        if isinstance(image, Path) and not image.exists():
            raise FileNotFoundError(image)


def read_conf() -> ConfigFile:  # type: ignore
    if os.getenv("UP2B_TEST"):
        return {}

    if not CONF_FILE.exists():
        logger.warning(
            "the configuration file is not found, "
            + "you need to use `--choose-site` or `-c` to select the image bed first."
        )

        return {}

    try:
        with CONF_FILE.open(encoding="utf-8") as f:
            conf: ConfigFile = json.loads(f.read())
    except Exception as e:
        logger.fatal("unkown error", err=e)
    else:
        return conf


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
                code=instance.image_bed_code,
            )

        return partial(self, instance)


def is_ascii(char: str):
    assert len(char) == 1, "只能处理字符，而不是字符串"
    return ord(char) < 128


def get_default_language() -> str:
    """默认使用中文，反正也没老外用。

    :returns: 语言标识
    :rtype: str
    """
    if IS_MACOS and PYTHON_VERSION < (3, 7, 5):
        logger.warning(
            f"the version [ {PYTHON_VERSION} ] below 3.7.5 on the macOS platform cannot obtain the system locale, and [ en_US ] is used by default."
        )
        lang = None
    else:
        sys_locale = locale.getdefaultlocale()

        logger.debug(f"system locale: {sys_locale}")

        lang = sys_locale[0]

    # return lang if lang else "en_US"
    return lang if lang else "zh_CN"


def is_url(path: str) -> bool:
    if not path.startswith("http"):
        return False

    try:
        urlparse(path)
        return True
    except ValueError:
        return False


def download_online_image(url: str):
    logger.debug("下载在线图片", url=url)

    resp = requests.get(url)
    if resp.status_code != 200:
        logger.error("在线图片下载失败", status_code=resp.status_code, body=resp.text)
        return DownloadErrorResponse(resp.status_code, resp.text)

    filename = os.path.basename(url)

    if not CACHE_PATH.exists():
        CACHE_PATH.mkdir()

    cache_path = CACHE_PATH / filename

    with cache_path.open("wb") as fb:
        fb.write(resp.content)

    logger.debug("在线图片已保存到缓存目录", cache_path=cache_path)

    return cache_path


def check_path(path: Union[Path, str]):
    if not is_url(str(path)):
        logger.debug("不是在线图片", path=path)
        return Path(path)

    logger.info("是在线图片", path=path)

    return download_online_image(str(path))


def check_paths(paths: Union[Sequence[str], Sequence[Path]]):
    if len(paths) == 1:
        return [check_path(Path(paths[0]))]

    new_paths: List[Union[Path, DownloadErrorResponse]] = [Path()] * len(paths)
    logger.info("使用线程池下载多张图片...")
    with ThreadPoolExecutor(4) as pool:
        futures = {
            pool.submit(check_path, Path(paths[0])): i for i in range(len(paths))
        }

        for future in as_completed(futures):
            idx = futures[future]
            data = future.result()
            new_paths[idx] = data

    logger.info("检查结果", original_paths=paths, new_paths=new_paths)

    return new_paths
