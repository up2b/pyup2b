#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author:      thepoy
# @Email:       thepoy@163.com
# @File Name:   __init__.py
# @Created At:  2021-02-08 15:43:32
# @Modified At: 2023-03-02 19:18:00
# @Modified By: thepoy

import os
import shutil
import sys
import json
import click

from typing import Any, Dict, Optional, Type, Union
from pprint import pprint
from colort import display_style as ds, DisplayStyle
from up2b.up2b_lib.custom_types import AuthData, ErrorResponse
from up2b.up2b_lib.i18n import read_i18n
from up2b.up2b_lib.up2b_api import choose_image_bed
from up2b.up2b_lib.up2b_api.sm import SM
from up2b.up2b_lib.up2b_api.imgtu import Imgtu
from up2b.up2b_lib.up2b_api.github import Github
from up2b.up2b_lib.up2b_api.imgtg import Imgtg
from up2b.up2b_lib.constants import (
    CACHE_PATH,
    CONF_FILE,
    IMAGE_BEDS_HELP_MESSAGE,
    IS_WINDOWS,
    ImageBedCode,
    IMAGE_BEDS_CODE,
)
from up2b.up2b_lib.utils import check_path, check_paths, read_conf
from up2b.up2b_lib.log import logger
from up2b.version import __version__  # Automatically create version.py after building

IMAGE_BEDS: Dict[
    ImageBedCode, Union[Type[SM], Type[Imgtu], Type[Github], Type[Imgtg]]
] = {
    ImageBedCode.SM_MS: SM,
    ImageBedCode.IMGTU: Imgtu,
    ImageBedCode.GITHUB: Github,
    ImageBedCode.IMGTG: Imgtg,
}


def echo(*args: Any):
    click.echo(" ".join([str(i) for i in args]))


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(name="cli", context_settings=CONTEXT_SETTINGS)
@click.help_option("-h", "--help", help="显示本帮助信息")
@click.version_option(
    __version__, "-v", "--version", message="%(version)s", help="显示版本信息"
)
def cli():
    pass


@cli.command(help="显示正在使用的图床")
def current():
    click.echo(
        f"""{ds.format_with_one_style(" " + chr(10003), ds.foreground_color.green)} {_read_image_bed(False, False)}""",
    )


@cli.command(help="列出支持的所有图床")
def list():
    print_list()


@cli.command(
    short_help="选择图床",
    help=f"""图床代码对应如下：\n\n{IMAGE_BEDS_HELP_MESSAGE}""",
)
@click.help_option("-h", "--help", help="显示本帮助信息")
@click.argument(
    "code",
    nargs=1,
    type=int,
    metavar="<int>",
)
def choose(code: int):
    choose_image_bed(code)
    echo(
        ds.format_with_one_style(" ==>", ds.foreground_color.cyan),
        IMAGE_BEDS[ImageBedCode(code)](),
    )


@cli.command(help="保存图床登录信息")
@click.help_option("-h", "--help", help="显示本帮助信息")
@click.argument(
    "username",
    nargs=1,
    type=str,
)
@click.argument(
    "password",
    nargs=1,
    type=str,
)
def login(username: str, password: str):
    print(username, password)


@cli.command(help="保存 git 登录信息")
@click.help_option("-h", "--help", help="显示本帮助信息")
@click.argument(
    "access_token",
    nargs=1,
    type=str,
)
@click.argument(
    "username",
    nargs=1,
    type=str,
)
@click.argument(
    "repository",
    nargs=1,
    type=str,
)
@click.argument(
    "path",
    nargs=1,
    type=str,
)
def login_git(access_token: str, username: str, repository: str, path: str):
    pass


@cli.command(help="上传一张图片")
@click.argument(
    "image_path",
    nargs=1,
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
)
@click.option(
    "-aw",
    "--add-watermark",
    type=bool,
    default=False,
    help="对要上传的图片添加文字水印",
)
@click.option(
    "-ac",
    "--auto-compress",
    type=bool,
    default=False,
    help="允许自动压缩图片",
)
def upload(image_path: str, add_watermark: bool, auto_compress: bool):
    print(type(image_path), add_watermark, auto_compress)


@cli.command(help="上传多张片")
@click.argument(
    "image_paths",
    nargs=-1,
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    metavar="[IMAGE_PATH]...",
)
@click.option(
    "-aw",
    "--add-watermark",
    type=bool,
    default=False,
    help="对要上传的图片添加文字水印",
)
@click.option(
    "-ac",
    "--auto-compress",
    type=bool,
    default=False,
    help="允许自动压缩图片",
)
def upload_images(image_paths: str, add_watermark: bool, auto_compress: bool):
    print(type(image_paths), add_watermark, auto_compress)


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
) -> Union[SM, Imgtu, Imgtg, Github]:
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


def print_list() -> int:
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

    def print_item(symbol, color, idx):
        ib = IMAGE_BEDS[ImageBedCode(idx)]()
        click.echo(
            f"""{ds.format_with_one_style(" " + symbol, color)} {idx} {ib}: {ib.description}"""
        )

    for i in ImageBedCode:
        if auth_data.get(str(i)):
            print_item(chr(10003), ds.fc.green, i)
        else:
            print_item(chr(10007), ds.fc.red, i)

    return 0


def run_main():
    with logger:
        sys.exit(cli())


if __name__ == "__main__":
    run_main()
