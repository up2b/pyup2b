#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author:      thepoy
# @Email:       thepoy@163.com
# @File Name:   errors.py
# @Created At:  2021-02-08 17:04:25
# @Modified At: 2023-02-21 12:41:08
# @Modified By: thepoy


class UploadFailed(Exception):
    pass


class OverSizeError(ValueError):
    pass


class NotLogin(NotImplementedError):
    pass


class UnsupportedType(TypeError):
    pass


class MissingAuth(ValueError):
    pass
