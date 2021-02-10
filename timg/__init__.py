#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: thepoy
# @Email: thepoy@aliyun.com
# @File Name: __init__.py
# @Created: 2021-02-08 15:43:32
# @Modified: 2021-02-10 17:12:34

import os
import sys
import json
import argparse

from typing import Union

from timg.timglib import timg_api

__version__ = '0.0.2'

IMAGE_BEDS = {
    "sm": timg_api.SM,
    "chr": timg_api.Chr,
}


def _BuildParser():
    parser = argparse.ArgumentParser(description='''
        A module that can upload pictures to the image bed in Typora.
        ''')
    parser.add_argument('-v',
                        '--version',
                        action='version',
                        version=__version__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--choose-site",
                       "-c",
                       choices=("sm", "chr"),
                       help="Choose the image bed you want to use.",
                       type=str)
    group.add_argument(
        "--login",
        "-l",
        nargs=2,
        help='''Save the user authentication token after successful login.
        You must enter the username and password after `-l` or `--login`,
        such as "timg -l username password".''',
        type=str)
    group.add_argument("--image-path",
                       "-p",
                       help="Upload only one picture.",
                       type=str)
    group.add_argument(
        "--images-path",
        "-ps",
        help='''Upload multiple pictures, the maximum is 10 pictures.
        Use spaces to separate each image path.''',
        nargs="+",
        type=str)

    return parser


def _read_image_bed() -> Union[timg_api.SM, timg_api.Chr]:
    try:
        with open(timg_api.CONF_FILE) as f:
            conf = json.loads(f.read())
            return IMAGE_BEDS[conf["image_bed"]]()
    except FileNotFoundError:
        print(
            "Error: The configuration file is not found, you need to use `--choose-site` or `-c` to select the image bed first."
        )
        sys.exit(1)


def main() -> int:

    args = _BuildParser().parse_args()

    if args.choose_site:
        timg_api.choose_image_bed(args.choose_site)
        return 0

    ib = _read_image_bed()

    if args.login:
        # If more than two parameters are given, only the first two are taken.
        ib.login(args.login[0], args.login[1])
        return 0

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
