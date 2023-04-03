#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author:      thepoy
# @Email:       thepoy@163.com
# @File Name:   log.py
# @Created At:  2023-02-07 12:13:41
# @Modified At: 2023-04-03 20:55:06
# @Modified By: thepoy

from colorful_logger import get_logger, child_logger as cl
from colorful_logger.logger import is_debug
from up2b.up2b_lib.constants import CONFIG_FOLDER_PATH

log_file_path = None
show = True

if is_debug():
    log_file_path = CONFIG_FOLDER_PATH / "up2b.log"
    show = True


def child_logger(name: str):
    return cl(name, logger)


logger = get_logger(
    "up2b",
    show=show,
    file_path=log_file_path,
    add_file_path=False,
    disable_line_number_filter=True,
    asynchronous=False,
)
