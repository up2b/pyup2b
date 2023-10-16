#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from colorful_logger import get_logger, child_logger as cl
from colorful_logger.logger import get_level_from_env
from up2b.up2b_lib.constants import CONFIG_FOLDER_PATH

log_file_path = CONFIG_FOLDER_PATH / "up2b.log"


def child_logger(name: str):
    return cl(name, logger)


logger = get_logger(
    "up2b",
    level=get_level_from_env(),
    file_path=log_file_path,
    add_file_path=False,
    disable_line_number_filter=True,
    asynchronous=False,
)
