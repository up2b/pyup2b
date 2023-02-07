#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author:    thepoy
# @Email:     thepoy@163.com
# @File Name: test_utils.py
# @Created:   2023-02-07 10:48:08
# @Modified:  2023-02-07 10:59:28

from tests import IMAGES
from up2b.up2b_lib import utils
from up2b.up2b_lib.constants import CACHE_PATH
from up2b.up2b_lib.custom_types import DownloadErrorResponse


class TestUtils:
    def test_is_url(self):
        yes = utils.is_url(str(IMAGES[0]))
        assert yes == False

        yes = utils.is_url("https://i.imgtg.com/2023/01/17/test.png")
        assert yes == True

    def test_check_path(self):
        path = utils.check_path(str(IMAGES[0]))
        assert IMAGES[0] == path

        path = utils.check_path("https://i.imgtg.com/2023/01/17/Qs1Vp.png")
        assert CACHE_PATH / "Qs1Vp.png" == path

        path = utils.check_path("https://i.imgtg.com/2023/01/17/test.png")
        assert isinstance(path, DownloadErrorResponse)
