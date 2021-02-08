#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: thepoy
# @Email: thepoy@aliyun.com
# @File Name: __init__.py
# @Created: 2021-02-08 15:43:32
# @Modified: 2021-02-08 21:40:49

import os
import sys
import argparse

from timg.timglib import timg_api

__version__ = '0.0.1'


def _BuildParser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v',
                        '--version',
                        action='version',
                        version=__version__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--login",
        "-l",
        nargs=2,
        help='''Save the user authentication token after successful login.
        You must enter the username and password after `-l` or `--login`,
        such as "timg -l username password"''',
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


def main():
    sm = timg_api.SM()

    args = _BuildParser().parse_args()

    if args.login:
        sm.login(args.login[0], args.login[1])
        return

    if args.image_path:
        if not os.path.exists(args.image_path):
            raise FileNotFoundError(f"{args.image_path}")

        sm.upload_image(args.image_path)
        return

    if args.images_path:
        sm.upload_images(args.images_path)
        return


def run_main():
    sys.exit(main())


if __name__ == '__main__':
    run_main()
