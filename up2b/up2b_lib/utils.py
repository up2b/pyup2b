#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: thepoy
# @Email: thepoy@163.com
# @File Name: utils.py
# @Created:  2021-02-09 15:17:32
# @Modified:  2022-01-09 10:47:23

import os
import locale

from functools import wraps, partial
from colorful_logger import get_logger, child_logger as cl
from colorful_logger.logger import DEBUG, ERROR


if os.getenv("DEBUG"):
    level = DEBUG
else:
    level = ERROR
logger = get_logger("up2b", level=level)


def child_logger(name: str):
    return cl(name, logger)


def check_image_exists(images_path: list):
    for image in images_path:
        if not os.path.exists(image):
            raise FileNotFoundError(image)


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
                "Error: You have not logged in yet, please use the `-l` or `--login` parameter to log in"
                " first.\nCurrent image bed code is : `%s`." % instance.image_bed_code
            )
        return partial(self, instance)


def is_ascii(src: str):
    assert len(src) == 1, "只能处理字符，而不是字符串"
    return ord(src) < 128


def get_default_language() -> str:
    lang = locale.getdefaultlocale()[0]
    return lang if lang else "en_US"
