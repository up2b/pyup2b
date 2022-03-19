#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author:    thepoy
# @Email:     thepoy@163.com
# @File Name: errors.py
# @Created:   2021-02-08 17:04:25
# @Modified:  2022-03-18 15:53:01


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
