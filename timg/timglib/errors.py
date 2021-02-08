#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: thepoy
# @Email: thepoy@aliyun.com
# @File Name: errors.py
# @Created: 2021-02-08 17:04:25
# @Modified: 2021-02-08 21:24:08


class UploadFailed(Exception):
    pass


class OverLimitError(Exception):
    pass
