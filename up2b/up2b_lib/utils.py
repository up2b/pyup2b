#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author:    thepoy
# @Email:     thepoy@163.com
# @File Name: utils.py
# @Created:   2021-02-09 15:17:32
# @Modified:  2022-03-10 10:39:47

import os
import locale

from functools import wraps, partial
from colorful_logger import get_logger, child_logger as cl
from colorful_logger.logger import is_debug

from up2b.up2b_lib.constants import CONFIG_FOLDER_PATH

log_file_path = None
print_position = False
show = True

if is_debug():
    log_file_path = os.path.join(CONFIG_FOLDER_PATH, "up2b.log")
    print_position = True
    show = False

logger = get_logger(
    "up2b",
    show=show,
    file_path=log_file_path,
    print_position=print_position,
)


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
                "you have not logged in yet, please use the `-l` or `--login` parameter to log in"
                + " first.\nCurrent image bed code is : `%s`.",
                instance.image_bed_code,
            )

        return partial(self, instance)


def is_ascii(char: str):
    assert len(char) == 1, "只能处理字符，而不是字符串"
    return ord(char) < 128


def get_default_language() -> str:
    sys_locale = locale.getdefaultlocale()

    logger.debug(f"system locale: {sys_locale}")

    lang = sys_locale[0]

    return lang if lang else "en_US"
