#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author:    thepoy
# @Email:     thepoy@163.com
# @File Name: test_github.py
# @Created:   2022-06-02 11:22:37
# @Modified:  2022-06-02 12:00:07


from tests import IMAGES
from up2b.up2b_lib.up2b_api.github import Github


class TestGithub:
    uploader = Github()

    def test_upload(self):
        url = self.uploader.upload_image(IMAGES[0])
        assert isinstance(url, str)

        assert url.startswith(
            f"https://cdn.jsdelivr.net/gh/{self.uploader.username}/{self.uploader.repo}/{self.uploader.folder}"
        )
