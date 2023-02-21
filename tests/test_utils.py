#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author:      thepoy
# @Email:       thepoy@163.com
# @File Name:   test_utils.py
# @Created At:  2023-02-07 10:48:08
# @Modified At: 2023-02-21 13:31:06
# @Modified By: thepoy

from tests import IMAGES
from up2b.up2b_lib import utils
from up2b.up2b_lib.constants import CACHE_PATH
from up2b.up2b_lib.custom_types import DownloadErrorResponse


class TestUtils:
    def test_is_url(self):
        yes = utils.is_url(str(IMAGES[0]))
        assert yes == False

        yes = utils.is_url(
            "https://raw.githubusercontent.com/thep0y/image-bed/main/test/test.jpg"
        )
        assert yes == True

    def test_check_path(self):
        path = utils.check_path(str(IMAGES[0]))
        assert IMAGES[0] == path

        path = utils.check_path(
            "https://raw.githubusercontent.com/thep0y/image-bed/main/test/1647607453268.jpg"
        )
        assert CACHE_PATH / "1647607453268.jpg" == path

        path = utils.check_path(
            "https://raw.githubusercontent.com/thep0y/image-bed/main/test/test.jpg"
        )
        assert isinstance(path, DownloadErrorResponse)
