#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author:    thepoy
# @Email:     thepoy@163.com
# @File Name: watermark.py
# @Created:   2021-02-09 15:17:32
# @Modified:  2022-03-24 20:05:42

import os

from up2b.up2b_lib.utils import child_logger

logger = child_logger(__name__)

try:
    from PIL import Image, ImageDraw, ImageFont, ImageEnhance
    from PIL.ImageDraw import ImageDraw as Draw
except ModuleNotFoundError:
    logger.fatal(
        "you have enabled the feature of adding watermark, but [ pillow ] is not installed, please execute `pip install pillow` before enabling this feature"
    )

from typing import List, Tuple
from collections import namedtuple

from up2b.up2b_lib.constants import CACHE_PATH
from up2b.up2b_lib.utils import is_ascii

TypeFont = namedtuple("TypeFont", ["text", "size", "font_path", "color"])


class AddWatermark:
    """添加水印的类

    可以向一张或多张图片添加文字或图片水印
    """

    def __init__(self, x: int, y: int, opacity: int = 50):
        """初始化函数

        初始化时，可以传入水印位置、输入路径和透明度

        Arguments:
            position {Tuple[int, int]} -- 水印的位置

        Keyword Arguments:
            output {str} -- 添加水印的图片的保存路径 (default: {"output/"})
            opacity {int} -- 透明度，整型，范围在 [0, 100] ，代表百分比 (default: {50})
        """
        self.x = x
        self.y = y
        self._step = self.y
        assert opacity >= 0 and opacity <= 100, "透明度只能在 0 到 100 之间"
        self.opacity = opacity

    def __set_opacity(self, img: Image.Image) -> Image.Image:
        """设置水印透明度

        Arguments:
            img {Image.Image} -- 要处理的图片对象

        Returns:
            Image.Image -- 已处理好的透明的img
        """
        alpha = img.split()[3]
        alpha = ImageEnhance.Brightness(alpha).enhance(self.opacity / 100)
        img.putalpha(alpha)
        return img

    def __text_watermark_position_handler(
        self, offset: float, size: int, img: Image.Image
    ) -> Tuple[float, int]:
        """设置文字水印位置

        水印坐标(x, y)（水印的参考点为左上角）
            当x, y >= 0 时，水印坐标从左上角按x、y的值移动到指定位置，
            当x < 0 且 y >= 0 时，水印从右上角移动，
            当x >= 0 且 y < 0 时，水印从右下角移动，
            当x，y < 0时，水印从左下角移动。

        Arguments:
            count {int} -- 水印文字的数量
            size {int} -- 字体大小
            img {Image.Image} -- 需要添加水印的图片对象

        Returns:
            Tuple[int, int] -- 计算后的真实坐标
        """
        width, height = img.size
        x, y = self.x, self.y

        if x < 0:
            x = x + width - offset
        if y < 0:
            y = y + height - size
        return x, y

    def __image_watermark_postion_handler(
        self, img: Image.Image, mark: Image.Image
    ) -> Tuple[float, int]:
        """设置图片水印的位置

        水印坐标(x, y)（水印的参考点为左上角）
            当x, y >= 0 时，水印坐标从左上角按x、y的值移动到指定位置，
            当x < 0 且 y >= 0 时，水印从右上角移动，
            当x >= 0 且 y < 0 时，水印从右下角移动，
            当x，y < 0时，水印从左下角移动。

        Arguments:
            img {Image.Image} -- 需添加水印的图片对象
            mark {Image.Image} -- 图片水印对象

        Returns:
            Tuple[int, int] -- 计算后的真实坐标
        """
        x, y = self.x, self.y
        width, height = img.size
        mark_w, mark_h = mark.size

        if x < 0:
            x = x + width - mark_w
            self.x = x
        if y < 0:
            y = y + height - mark_h
            self.y = y
        return x, y

    def _cal_x_offset(self, text: str, size: int) -> float:
        offset = 0.0
        for c in text:
            if is_ascii(c):
                offset += size / 2
            else:
                offset += size
        return offset

    def __convert_image_to_rgba(self, image_path: str) -> Image.Image:
        img = Image.open(image_path)
        return img.convert("RGBA")

    def __draw_text(self, img: Image.Image, draw: Draw, tf: TypeFont):
        offset = self._cal_x_offset(tf.text, tf.size)
        position = self.__text_watermark_position_handler(offset, tf.size, img)
        if not tf.font_path:
            raise ValueError("font path is required")
        ftf = ImageFont.truetype(tf.font_path, size=tf.size)
        draw.text(position, tf.text, font=ftf, fill=tf.color)  # 将文字填充到字体图层

    def add_text_watermark(
        self,
        image_path: str,
        texts: List[TypeFont],
    ) -> str:
        img = self.__convert_image_to_rgba(image_path)

        watermark = Image.new("RGBA", img.size, (0, 0, 0, 0))  # 字体图层

        draw = ImageDraw.Draw(watermark)  # 创建文字水印编辑对象
        texts.reverse()
        for text in texts:
            self.__draw_text(img, draw, text)
            self.y += self._step
        watermark = self.__set_opacity(watermark)  # 设置水印透明度
        del draw  # 删除文字水印编辑对象

        combined = Image.alpha_composite(img, watermark)  # 将原图和字体图层合并
        combined = combined.convert("RGB")
        filename = os.path.splitext(os.path.basename(image_path))[0] + ".jpg"

        if not os.path.exists(CACHE_PATH):
            os.mkdir(CACHE_PATH)

        new_path = os.path.join(CACHE_PATH, filename)

        combined.save(os.path.join(CACHE_PATH, filename))

        return new_path

    def add_image_watermark(
        self,
        image_path: str,
        image_watermark_path: str,
        resize: int = 100,
    ):
        """添加图片水印

        添加指定位置、透明度、输出路径、缩放比例和图片水印

        Arguments:
            image_path {str} -- 要添加水印的图片路径
            image_watermark_path {str} -- 要添加和水印路径

        Keyword Arguments:
            resize {int} -- 缩放比例，范围在 [0, 100] 之间的整数，是一个百分比，默认值为100，即为不缩放 (default: {100})
            suffix {str} -- 添加水印图片后的文件名后缀 (default: {"_with_image_watermark"})
        """
        img = self.__convert_image_to_rgba(image_path)
        mark: Image.Image = Image.open(image_watermark_path)

        mark_w, mark_h = mark.size
        mark = mark.resize((int(mark_w * resize / 100), int(mark_h * resize / 100)))

        position = self.__image_watermark_postion_handler(img, mark)

        watermark = Image.new("RGBA", img.size, (0, 0, 0, 0))
        watermark.paste(mark, position)
        watermark = self.__set_opacity(watermark)

        combined = Image.alpha_composite(img, watermark)
        combined = combined.convert("RGB")
        filename = os.path.splitext(os.path.basename(image_path))[0] + ".jpg"

        combined.save(os.path.join(CACHE_PATH, filename))
