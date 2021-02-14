#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: thepoy
# @Email: thepoy@163.com
# @File Name: custom_types.py
# @Created:  2021-02-09 11:27:21
# @Modified: 2021-02-14 15:16:55

from typing import Dict, Union

AuthInfo = Dict[str, str]
DeletedResponse = Dict[str, Union[bool, str]]
