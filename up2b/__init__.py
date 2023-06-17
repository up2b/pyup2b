#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author:      thepoy
# @Email:       thepoy@163.com
# @File Name:   __init__.py
# @Created At:  2021-02-08 15:43:32
# @Modified At: 2023-04-19 14:45:15
# @Modified By: thepoy

import sys
import json
import click

from typing import Any, Dict, Optional, Tuple, Type, Union
from colort import display_style as ds
from up2b.up2b_lib.custom_types import AuthData
from up2b.up2b_lib.up2b_api import choose_image_bed
from up2b.up2b_lib.up2b_api.sm import SM
from up2b.up2b_lib.up2b_api.imgtu import Imgtu
from up2b.up2b_lib.up2b_api.github import Github
from up2b.up2b_lib.up2b_api.imgtg import Imgtg
from up2b.up2b_lib.constants import (
    CACHE_PATH,
    CONF_FILE,
    IMAGE_BEDS_HELP_MESSAGE,
    ImageBedCode,
)
from up2b.up2b_lib.utils import check_paths, read_conf
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
    if not CACHE_PATH.exists():
        logger.debug("缓存目录不存在")
        CACHE_PATH.mkdir()
        logger.info("已创建缓存目录", cache_path=CACHE_PATH)


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
    ib = _read_image_bed()
    if isinstance(ib, Github):
        logger.fatal(
            "you have chosen `github` as the image bed, please login with `-lg`"
        )

    logger.info("current image bed", name=ib)

    echo("正在验证账号，请耐心等待...")

    ok = ib.login(username, password)
    if not ok:
        logger.fatal("username or password incorrect")

    echo("账号验证通过")


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
    ib = _read_image_bed()
    if not isinstance(ib, Github):
        logger.fatal(
            "the image bed you choose is not `github`, , please login with `-l`"
        )

    ib.login(access_token, username, repository, path)


@cli.command(help="上传图片")
@click.argument(
    "image_paths",
    nargs=-1,
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    metavar="[IMAGE_PATH]...",
)
@click.option(
    "-aw",
    "--add-watermark",
    is_flag=True,
    show_default=True,
    default=False,
    help="对要上传的图片添加文字水印",
)
@click.option(
    "-ac",
    "--auto-compress",
    is_flag=True,
    show_default=True,
    default=False,
    help="允许自动压缩图片",
)
@click.option(
    "-ic",
    "--ignore-cache",
    is_flag=True,
    show_default=True,
    default=False,
    help="忽略数据库缓存，强制上传图片",
)
def upload(
    image_paths: Tuple[str],
    add_watermark: bool,
    auto_compress: bool,
    ignore_cache: bool,
):
    ib = _read_image_bed(
        add_watermark=add_watermark,
        auto_compress=auto_compress,
        ignore_cache=ignore_cache,
    )

    paths = check_paths(image_paths)

    ib.upload_images(*paths)


@cli.command(
    short_help="配置文字水印",
    help="""
    参数解释：

        - x 整数，横坐标
    
        - y 整数，纵坐标
    
        - opacity 整数，透明度。50 即为透明度 50%。
    
        - text 字符串，水印文字内容
    
        - font_path 字符串，字体路径
    
        - size 整数，字体大小
    """,
)
@click.argument(
    "x",
    nargs=1,
    type=int,
)
@click.argument(
    "y",
    nargs=1,
    type=int,
)
@click.argument(
    "opacity",
    nargs=1,
    type=int,
)
@click.argument(
    "text",
    nargs=1,
    type=str,
)
@click.argument(
    "font_path",
    nargs=1,
    type=str,
)
@click.argument(
    "size",
    nargs=1,
    type=int,
)
def config_watermark(
    x: int, y: int, opacity: int, text: str, font_path: str, size: int
):
    _config_text_watermark(x, y, opacity, text, font_path, size)


def _read_image_bed(
    auto_compress: bool = False,
    add_watermark: bool = False,
    ignore_cache: bool = False,
) -> Union[SM, Imgtu, Imgtg, Github]:
    conf = read_conf()

    selected_code = conf.get("image_bed")
    if not selected_code:
        logger.fatal("当前图床为空，请先选择要使用的图床")

    assert isinstance(selected_code, int)

    try:
        code = ImageBedCode(selected_code)

        return IMAGE_BEDS[code](
            auto_compress=auto_compress,
            add_watermark=add_watermark,
            ignore_cache=ignore_cache,
        )
    except ValueError:
        IMAGE_BEDS[ImageBedCode.SM_MS](
            auto_compress=auto_compress,
            add_watermark=add_watermark,
            ignore_cache=ignore_cache,
        )
        logger.fatal("未知的图床代码，可能因为清除无效的 gitee 配置，请重试", code=selected_code)


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
    auth_data: AuthData = conf.get("auth_data", {})  # type: ignore

    if not auth_data:
        selected_code = conf.get("image_bed")
        if selected_code is None:
            logger.warning(
                "no image bed selected, "
                + "you need to use `--choose-site` or `-c` to select the image bed first."
            )

        if selected_code:
            code = ImageBedCode(selected_code)

            logger.warning(
                "no authentication information has been configured",
                image_bed=ds.format_with_multiple_styles(
                    IMAGE_BEDS[code]().__str__(),
                    ds.backgorud_color.dark_gray,
                    ds.foreground_color.white,
                ),
                code=selected_code,
            )

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
    sys.exit(cli())


if __name__ == "__main__":
    run_main()
