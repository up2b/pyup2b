#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author:    thepoy
# @Email:     thepoy@163.com
# @File Name: i18n.py
# @Created:   2022-01-09 11:17:23
# @Modified:  2022-04-02 22:51:15

import json
import os
from typing import Dict


from up2b.up2b_lib.constants import CONFIG_FOLDER_PATH
from up2b.up2b_lib.utils import get_default_language, child_logger

logger = child_logger(__name__)

_i18n_folder = os.path.join(CONFIG_FOLDER_PATH, "i18n")

LangType = str
English = str
Translation = str
Locale = Dict[English, Translation]

_i18ns: Dict[LangType, Locale] = {
    "en_US": {
        "A package that can upload images to the image bed.": "A package that can upload images to the image bed.",
        "allow automatic image compression": "allow automatic image compression",
        "whether to add text watermark to the images to be uploaded": "whether to add text watermark to the images to be uploaded",
        "show the image bed in use": "show the image bed in use",
        "list all configured image beds": "list all configured image beds",
        "choose the image bed you want to use and exit": "choose the image bed you want to use and exit",
        "save the user authentication token after successful login. You must enter the username and password after `-l` or `--login`": "save the user authentication token after successful login. You must enter the username and password after `-l` or `--login`",
        "save the authentication information of the git website, such as github": "save the authentication information of the git website, such as github",
        "configure the text watermark": "configure the text watermark",
        "upload only one picture": "upload only one picture",
        "upload multiple pictures, the maximum is 10 pictures, use spaces to separate each image path": "upload multiple pictures, the maximum is 10 pictures, use spaces to separate each image path",
        "save the authentication information of coding": "save the authentication information of coding",
    },
    "zh_CN": {
        "A package that can upload images to the image bed.": "一个能将本地图片压缩、加水印或原图上传到图床的包",
        "allow automatic image compression": "允许自动压缩图片。开启此项后，超过图床限制大小的图片将会自动压缩到限制大小后再上传",
        "whether to add text watermark to the images to be uploaded": "对要上传的图片添加文字水印",
        "show the image bed in use": "显示正在使用的图床",
        "list all configured image beds": "列出所有已配置的图床",
        "choose the image bed you want to use and exit": "选择要使用的图床",
        "save the user authentication token after successful login. You must enter the username and password after `-l` or `--login`": "保存认证信息。你需要在`-l`或`--login`后输入账名和密码",
        "save the authentication information of the git website, such as github": "保存 git 类型图床的认证信息，如 github",
        "configure the text watermark": "配置要添加的文字水印",
        "upload only one picture": "上传一张图片",
        "upload multiple pictures, the maximum is 10 pictures, use spaces to separate each image path": "上传多张图片。多张图片路径之间以空格分隔，最多能上传 10 张",
        "save the authentication information of coding": "保存 Coding 的认证信息",
    },
}


def read_i18n() -> Locale:
    if not os.path.exists(_i18n_folder):
        os.mkdir(_i18n_folder)

        logger.debug("the language used: [ en_US ]")

        return _i18ns["en_US"]

    lang = get_default_language()
    locale = _i18ns.get(lang)
    if locale:
        logger.debug("the language used: [ %s ]", lang)
        return locale

    translation_file = os.path.join(_i18n_folder, lang + ".json")
    if not os.path.exists(translation_file):
        logger.info(
            "the language used is [ %s ], but no translation file for [ %s ] was found, so use [ en_US ]",
            lang,
            lang,
        )
        return _i18ns["en_US"]

    logger.debug("translation file [ %s ] will be used", translation_file)
    return json.loads(translation_file)
