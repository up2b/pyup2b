#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: thepoy
# @Email: thepoy@aliyun.com
# @File Name: test_imgtu.py
# @Created: 2021-02-11 08:59:33
# @Modified:  2022-06-02 12:22:30


from tests import IMAGES
from up2b.up2b_lib.up2b_api.imgtu import Imgtu


class TestImgtu:
    uploader = Imgtu()

    def test_upload(self):
        url = self.uploader.upload_image(IMAGES[0])
        assert isinstance(url, str)

        assert url.startswith("https://s1.ax1x.com/")
