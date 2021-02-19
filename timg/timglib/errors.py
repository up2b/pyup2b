#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: thepoy
# @Email: thepoy@aliyun.com
# @File Name: errors.py
# @Created: 2021-02-08 17:04:25
# @Modified: 2021-02-17 15:55:12


class UploadFailed(Exception):
    pass


class OverSizeError(Exception):
    pass


class NotLogin(Exception):
    pass


class UnsupportedType(TypeError):
    pass
