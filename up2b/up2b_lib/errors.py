#!/usr/bin/env python3
# -*- coding:utf-8 -*-


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


class Timeout(Exception):
    pass
