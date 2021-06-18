#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: thepoy
# @Email: thepoy@aliyun.com
# @File Name: test_imgtu.py
# @Created: 2021-02-11 08:59:33
# @Modified: 2021-06-18 11:06:34

import sys

sys.path.append("../")

import json
import os
from unittest import TestCase

import up2b
from up2b.up2b_lib.constants import IMGTU
from up2b.up2b_lib.up2b_api.imgtu import Imgtu

# from fixtures import TestCaseUp2b

CONFIG_FILE = "./up2b.json"
IMAGES_FOLDER = "./images"

os.environ.setdefault("UP2B_TEST", "1")


class TestUp2bImgtu(TestCase):
    def setUp(self) -> None:
        self.imgtu = Imgtu(CONFIG_FILE)
        self.assertIsNotNone(self.imgtu.cookie)
        self.assertIsNotNone(self.imgtu.token)
        return super().setUp()

    def _choose_image_bed(self, code: int):
        up2b.choose_image_bed(code, CONFIG_FILE)
        with open(CONFIG_FILE) as f:
            config = json.loads(f.read())
        self.assertEqual(config["image_bed"], code)

    def test_choose_image_bed(self):
        with open(CONFIG_FILE) as f:
            config = json.loads(f.read())
        if config.get("image_bed") != IMGTU:
            self._choose_image_bed(IMGTU)
        else:
            self._choose_image_bed(0)
            self._choose_image_bed(IMGTU)

    def test_upload_and_delete_a_image(self):
        result = self.imgtu.upload_image(os.path.join(IMAGES_FOLDER, "1.png"))
        self.assertTrue(isinstance(result, str))

        img_id = os.path.basename(result).split(".")[0]

        delete_result = self.imgtu.delete_image(img_id)
        self.assertEqual(delete_result["status_code"], 200)

    def test_upload_and_delete_3_images(self):
        images = [
            os.path.join(IMAGES_FOLDER, "1.png"),
            os.path.join(IMAGES_FOLDER, "2.jpeg"),
            os.path.join(IMAGES_FOLDER, "3.jpeg"),
        ]
        upload_result = self.imgtu.upload_images(images)
        self.assertEqual(len(upload_result), 3)

        imgs_id = [os.path.basename(i).split(".")[0] for i in upload_result]

        delete_result = self.imgtu.delete_images(imgs_id)
        self.assertEqual(delete_result["status_code"], 200)
