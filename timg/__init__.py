#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: thepoy
# @Email: thepoy@aliyun.com
# @File Name: __init__.py
# @Created: 2021-02-08 15:43:32
# @Modified: 2021-02-19 11:07:52

import os
import sys
import json
import argparse

from typing import Union

from timg.timglib.timg_api import CONF_FILE, choose_image_bed
from timg.timglib.timg_api.sm import SM
from timg.timglib.timg_api.chr import Chr
from timg.timglib.timg_api.gitee import Gitee
from timg.timglib.timg_api.github import Github
from timg.timglib.constants import SM_MS, IMAGE_CHR, GITEE, GITHUB

__version__ = '0.0.9'

IMAGE_BEDS = {
    SM_MS: SM,
    IMAGE_CHR: Chr,
    GITEE: Gitee,
    GITHUB: Github,
}


def _BuildParser():
    parser = argparse.ArgumentParser(description=(
        'A package that can upload pictures to the image bed in Typora.'))
    parser.add_argument('-v',
                        '--version',
                        action='version',
                        version=__version__)
    parser.add_argument('-aac',
                        action='store_true',
                        help="allow automatic image compression")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-c",
                       "--choose-site",
                       choices=IMAGE_BEDS.keys(),
                       help="choose the image bed you want to use and exit",
                       type=str)
    group.add_argument(
        "-l",
        "--login",
        nargs=2,
        metavar=("USERNAME", "PASSWORD"),
        help=('save the user authentication token after successful login. You '
              'must enter the username and password after `-l` or `--login`'),
        type=str)
    group.add_argument(
        "-lg",
        "--login-git",
        nargs=4,
        metavar=("ACCESS_TOKEN", "USERNAME", "REPO", "FOLDER"),
        help=('save the authentication information of the git website, '
              'such as gitee, github'),
        type=str)
    group.add_argument("-p",
                       "--image-path",
                       help="upload only one picture",
                       type=str)
    group.add_argument(
        "-ps",
        "--images-path",
        metavar="IMAGE_PATH",
        nargs="+",
        help=('upload multiple pictures, the maximum is 10 pictures, '
              'use spaces to separate each image path.'),
        type=str)

    return parser


def _read_image_bed(auto_compress: bool) -> Union[SM, Chr]:
    try:
        with open(CONF_FILE) as f:
            conf = json.loads(f.read())
            return IMAGE_BEDS[conf["image_bed"]](auto_compress=auto_compress)
    except FileNotFoundError:
        print(
            "Error: The configuration file is not found, "
            "you need to use `--choose-site` or `-c` to select the image bed first."
        )
        sys.exit(1)


def main() -> int:

    args = _BuildParser().parse_args()

    if args.choose_site:
        choose_image_bed(args.choose_site)
        if args.choose_site == GITEE:
            print(
                "Warning: resources bigger than 1M on `gitee` cannot be publicly accessed. "
                "Please manually compress the image size to 1M or less, "
                "or use the `-aac` parameter to enable the automatic compression function."
            )
        return 0

    ib = _read_image_bed(args.aac)

    if args.login:
        if isinstance(ib, Gitee) or isinstance(ib, Github):
            print(
                "Error: you have chosen `gitee` or `github` as the image bed, please login with `-lg`"
            )
            return 1

        ib.login(*args.login)

        return 0

    if args.login_git:
        if not (isinstance(ib, Gitee) or isinstance(ib, Github)):
            print(
                "Error: the image bed you choose is not gitee or github, , please login with `-lg`"
            )
            return 1

        ib.login(*args.login_git)

    if args.image_path:
        if not os.path.exists(args.image_path):
            raise FileNotFoundError(f"{args.image_path}")

        ib.upload_image(args.image_path)
        return 0

    if args.images_path:
        ib.upload_images(args.images_path)
        return 0


def run_main():
    sys.exit(main())


if __name__ == '__main__':
    run_main()
