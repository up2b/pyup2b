#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: thepoy
# @Email: thepoy@163.com
# @File Name: utils.py
# @Created:  2021-02-09 15:17:32
# @Modified: 2021-02-20 19:30:08

import os
import sys

from functools import wraps, partial


def check_image_exists(images_path: list):
    for image in images_path:
        if not os.path.exists(image):
            raise FileNotFoundError(image)


class Login:
    def __init__(self, func):
        wraps(func)(self)

    def __call__(self, instance, *args, **kwargs):
        return self.__wrapped__(instance, *args, **kwargs)

    def __get__(self, instance, cls):
        if not instance:
            return partial(self, instance)

        if not instance.auth_info:
            print(
                "Error: You have not logged in yet, please use the `-l` or `--login` parameter to log in first.\nCurrent image bed code is : `%s`."
                % instance.image_bed_code)
            sys.exit(0)
        return partial(self, instance)
