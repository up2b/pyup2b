#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author:    thepoy
# @Email:     thepoy@aliyun.com
# @File Name: __init__.py
# @Created:   2021-02-08 15:43:32
# @Modified:  2022-04-14 10:08:09

import os
import shutil
import sys
import json
import argparse

from typing import Dict, Optional, Type, Union
from pprint import pprint
from colort import DisplayStyle
from up2b.up2b_lib.custom_types import AuthData
from up2b.up2b_lib.i18n import read_i18n
from up2b.up2b_lib.up2b_api import choose_image_bed
from up2b.up2b_lib.up2b_api.coding import Coding
from up2b.up2b_lib.up2b_api.sm import SM
from up2b.up2b_lib.up2b_api.imgtu import Imgtu
from up2b.up2b_lib.up2b_api.github import Github
from up2b.up2b_lib.constants import (
    CONF_FILE,
    IS_WINDOWS,
    ImageBedCode,
    IMAGE_BEDS_CODE,
)
from up2b.up2b_lib.utils import logger, read_conf

__version__ = "0.4.0"

IMAGE_BEDS: Dict[
    ImageBedCode, Union[Type[SM], Type[Imgtu], Type[Github], Type[Coding]]
] = {
    ImageBedCode.SM_MS: SM,
    ImageBedCode.IMGTU: Imgtu,
    ImageBedCode.GITHUB: Github,
    ImageBedCode.CODING: Coding,
}


def _BuildParser():
    locale = read_i18n()

    parser = argparse.ArgumentParser(
        description=locale["A package that can upload images to the image bed."]
    )
    parser.add_argument("-v", "--version", action="version", version=__version__)
    parser.add_argument(
        "-aac", action="store_true", help=locale["allow automatic image compression"]
    )
    parser.add_argument(
        "-aw",
        "--add-watermark",
        action="store_true",
        help=locale["whether to add text watermark to the images to be uploaded"],
    )
    parser.add_argument(
        "--current",
        action="store_true",
        help=locale["show the image bed in use"],
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help=locale["list all configured image beds"],
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-c",
        "--choose-site",
        choices=[str(k.value) for k in IMAGE_BEDS.keys()],
        metavar=str({v.value: k for k, v in IMAGE_BEDS_CODE.items()}),
        help=locale["choose the image bed you want to use and exit"],
        type=str,
    )
    group.add_argument(
        "-l",
        "--login",
        nargs=2,
        metavar=("USERNAME", "PASSWORD"),
        help=locale[
            "save the user authentication token after successful login. You must enter the username and password after `-l` or `--login`"
        ],
        type=str,
    )
    group.add_argument(
        "-lg",
        "--login-git",
        nargs=4,
        metavar=("ACCESS_TOKEN", "USERNAME", "REPO", "FOLDER"),
        help=locale[
            "save the authentication information of the git website, such as github"
        ],
        type=str,
    )
    group.add_argument(
        "-lc",
        "--login-coding",
        nargs=5,
        metavar=("ACCESS_TOKEN", "USERNAME", "PROJECT", "REPO", "FOLDER"),
        help=locale["save the authentication information of coding"],
        type=str,
    )
    group.add_argument(
        "--config-text-watermark",
        nargs=6,
        metavar=("X", "Y", "OPACITY", "TEXT", "FONT_PATH", "SIZE"),
        help=locale["configure the text watermark"],
        type=str,
    )
    group.add_argument(
        "-p", "--image-path", help=locale["upload only one picture"], type=str
    )
    group.add_argument(
        "-ps",
        "--images-path",
        metavar="IMAGE_PATH",
        nargs="+",
        help=locale[
            "upload multiple pictures, the maximum is 10 pictures, use spaces to separate each image path"
        ],
        type=str,
    )

    return parser


def _is_old_config_file(conf):
    if not conf.get("auth_data") or isinstance(conf["auth_data"], dict):
        return False

    print("!!!注意!!!")
    print()
    print(
        """
    由于 gitee 出乎我意料地停止了图床功能，我也无法保证现在的图床都能继续使用，最初设计配置文件时没有考虑到这一点。
    为了不影响以后对支持图床的增删，需要对配置文件进行重新设计，接下来的操作将会删除旧配置文件，如有需要请备份下面的配置信息，后面登录时会用到。
    """
    )
    print()
    print("配置信息（此消息仅显示一次）：")
    print("*" * 20)
    pprint(conf)
    print("*" * 20)
    return True


def _move_to_desktop():
    if IS_WINDOWS:
        home = os.environ["USERPROFILE"]
    else:
        home = os.environ["HOME"]

    dst = os.path.join(home, "Desktop")
    if not os.path.exists(dst):
        dst = home

    shutil.move(CONF_FILE, os.path.join(dst, "up2b-backup.json"))


def _read_image_bed(
    auto_compress: bool, add_watermark: bool
) -> Union[SM, Imgtu, Github, Coding]:
    conf = read_conf()

    if _is_old_config_file(conf):
        _move_to_desktop()
        logger.warning("旧配置文件已移动到桌面（桌面不存在时移动到主目录），请重新选择图床并登录")
        sys.exit(0)

    selected_code = conf["image_bed"]
    assert isinstance(selected_code, int)

    try:
        code = ImageBedCode(selected_code)

        return IMAGE_BEDS[code](
            auto_compress=auto_compress, add_watermark=add_watermark
        )
    except ValueError:
        IMAGE_BEDS[ImageBedCode.SM_MS](
            auto_compress=auto_compress, add_watermark=add_watermark
        )
        logger.fatal("未知的图床代码：%d，可能因为清除无效的 gitee 配置，请重试", selected_code)


def _config_text_watermark(
    x: int, y: int, opacity: int, text: str, font: str, size: int
):
    try:
        with open(CONF_FILE, "r+") as f:
            conf = json.loads(f.read())
            f.seek(0, 0)
            conf["watermark"] = {
                "x": x,
                "y": y,
                "opacity": opacity,
                "text": text,
                "font": font,
                "size": size,
            }
            f.write(json.dumps(conf))
            f.truncate()
    except FileNotFoundError:
        with open(CONF_FILE, "w") as f:
            f.write(
                json.dumps(
                    {
                        "watermark": {
                            "x": x,
                            "y": y,
                            "opacity": opacity,
                            "text": text,
                            "font": font,
                            "size": size,
                        }
                    }
                )
            )


def print_list(ds: DisplayStyle) -> int:
    conf = read_conf()
    auth_data: Optional[AuthData] = conf.get("auth_data")  # type: ignore

    if not auth_data:
        selected_code = conf.get("image_bed", -1)
        if selected_code is None:
            logger.fatal(
                "no image bed selected, "
                + "you need to use `--choose-site` or `-c` to select the image bed first."
            )

        assert isinstance(selected_code, int)

        code = ImageBedCode(selected_code)

        logger.warning(
            "you have selected %s, but no authentication information has been configured.\n\n%s %s %s",
            ds.format_with_multiple_styles(
                " " + IMAGE_BEDS[code]().__str__() + " ",
                ds.backgorud_color.dark_gray,
                ds.foreground_color.white,
            ),
            ds.format_with_one_style(" " + chr(10007), ds.foreground_color.red),
            selected_code,
            IMAGE_BEDS[code](),
        )
        return 0

    for i in ImageBedCode:
        if auth_data.get(str(i)):
            print(
                ds.format_with_one_style(" " + chr(10003), ds.foreground_color.green),
                i,
                IMAGE_BEDS[ImageBedCode(i)](),
            )
        else:
            print(
                ds.format_with_one_style(" " + chr(10007), ds.foreground_color.red),
                i,
                IMAGE_BEDS[ImageBedCode(i)](),
            )
    return 0


def main() -> int:
    args = _BuildParser().parse_args()

    ds = DisplayStyle()

    if args.current:
        print(
            ds.format_with_one_style(" " + chr(10003), ds.foreground_color.green),
            _read_image_bed(False, False),
        )
        return 0

    if args.list:
        return print_list(ds)

    if args.choose_site:
        code = int(args.choose_site)
        choose_image_bed(code)
        print(
            ds.format_with_one_style(" ==>", ds.foreground_color.cyan),
            IMAGE_BEDS[ImageBedCode(code)](),
        )

        return 0

    if args.config_text_watermark:
        _args = args.config_text_watermark
        _config_text_watermark(
            int(_args[0]),
            int(_args[1]),
            100 - int(_args[2]),
            _args[3],
            _args[4],
            int(_args[5]),
        )
        return 0

    ib = _read_image_bed(args.aac, args.add_watermark)

    if args.login:
        if isinstance(ib, Github):
            logger.fatal(
                "you have chosen `github` as the image bed, please login with `-lg`"
            )
        if isinstance(ib, Coding):
            logger.fatal(
                "you have chosen `coding` as the image bed, please login with `-lc`"
            )

        logger.debug("current image bed: %s", ib)

        ok = ib.login(*args.login)
        if not ok:
            logger.fatal("username or password incorrect")

        return 0

    if args.login_coding:
        if not isinstance(ib, Coding):
            logger.fatal("you have not chosen `coding` as the image bed")

        logger.debug("current image bed: %s", ib)

        ok = ib.login(*args.login_coding)
        if not ok:
            logger.fatal("username or password incorrect")

        return 0

    if args.login_git:
        if not isinstance(ib, Github):
            logger.fatal(
                "the image bed you choose is not `github`, , please login with `-l`"
            )

        ib.login(*args.login_git)

    if args.image_path:
        if not os.path.exists(args.image_path):
            raise FileNotFoundError(f"{args.image_path}")

        ib.upload_image(args.image_path)
        return 0

    if args.images_path:
        ib.upload_images(*args.images_path)
        return 0

    return 1


def run_main():
    with logger:
        sys.exit(main())


if __name__ == "__main__":
    run_main()
