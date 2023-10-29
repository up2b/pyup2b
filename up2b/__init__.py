#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from dataclasses import asdict
import sys
import json
import click

from typing import Any, Dict, Optional, Tuple, Type, Union
from pathlib import Path
from colort import colorize, ForegroundColor, BackgroundColor
from up2b.up2b_lib.custom_types import WaterMarkConfig
from up2b.up2b_lib.up2b_api import choose_image_bed
from up2b.up2b_lib.up2b_api.sm import SM
from up2b.up2b_lib.up2b_api.imgtu import Imgtu
from up2b.up2b_lib.up2b_api.github import Github
from up2b.up2b_lib.up2b_api.imgtg import Imgtg
from up2b.up2b_lib.constants import (
    CACHE_PATH,
    CONF_FILE,
    IMAGE_BEDS_HELP_MESSAGE,
    IMAGE_BEDS_NAME,
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
        f"""{colorize(" " + chr(10004), ForegroundColor.GREEN)} {_read_image_bed(False, False)}""",
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
        colorize(" ==>", ForegroundColor.CYAN),
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

    logger.info("current image bed", name=str(ib))

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
@click.option(
    "-q",
    "--quiet",
    is_flag=True,
    show_default=True,
    default=False,
    help="静默模式。开启后不显示上传进度",
)
@click.option("-t", "--timeout", type=float, help="上传图片的超时时间")
def upload(
    image_paths: Tuple[str],
    add_watermark: bool,
    auto_compress: bool,
    ignore_cache: bool,
    timeout: float,
    quiet: bool,
):
    ib = _read_image_bed(
        add_watermark=add_watermark,
        auto_compress=auto_compress,
        ignore_cache=ignore_cache,
        timeout=timeout,
        quiet=quiet,
    )

    paths = check_paths(image_paths)

    ib.upload_images(*paths)


@cli.command(
    short_help="手动添加缓存", help="某些图床禁止上传重复图片，但在上传时又不返回旧图片地址，此时需要你手动获取原图片地址并执行此命令添加到缓存中。"
)
@click.argument(
    "image_path",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path),
)
@click.argument("url", type=str)
def add_cache(image_path: Path, url: str):
    ib = _read_image_bed()
    ib.cache.add(image_path, url, IMAGE_BEDS_NAME[ib.image_bed_code])


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
    type=click.Path(exists=True, dir_okay=False),
)
@click.argument(
    "size",
    nargs=1,
    type=int,
)
def config_watermark(
    x: int, y: int, opacity: int, text: str, font_path: str, size: int
):
    config = WaterMarkConfig(x, y, text, font_path, size, opacity)
    _config_text_watermark(config)


def _read_image_bed(
    auto_compress: bool = False,
    add_watermark: bool = False,
    ignore_cache: bool = False,
    timeout: Optional[float] = None,
    quiet: bool = False,
) -> Union[SM, Imgtu, Imgtg, Github]:
    conf = read_conf()

    selected_code = conf.image_bed
    if selected_code == None:
        logger.fatal("当前图床为空，请先选择要使用的图床")

    assert isinstance(selected_code, int)

    try:
        code = ImageBedCode(selected_code)

        return IMAGE_BEDS[code](
            auto_compress=auto_compress,
            add_watermark=add_watermark,
            ignore_cache=ignore_cache,
            timeout=timeout,
            quiet=quiet,
            conf=conf,
        )
    except ValueError:
        logger.fatal("未知的图床代码，可能因为清除无效的 gitee 配置，请重试", code=selected_code)


def _config_text_watermark(config: WaterMarkConfig):
    try:
        with open(CONF_FILE, "r+") as f:
            conf = json.loads(f.read())
            f.seek(0, 0)
            conf["watermark"] = asdict(config)
            f.write(json.dumps(conf))
            f.truncate()
    except FileNotFoundError:
        with open(CONF_FILE, "w") as f:
            f.write(json.dumps({"watermark": asdict(config)}))


def print_list() -> int:
    conf = read_conf()
    auth_data = conf.auth_data

    assert isinstance(auth_data, dict)

    if not auth_data:
        if conf.image_bed is None:
            logger.warning(
                "no image bed selected, "
                + "you need to use `--choose-site` or `-c` to select the image bed first."
            )

        if conf.image_bed:
            logger.warning(
                "no authentication information has been configured",
                image_bed=colorize(
                    IMAGE_BEDS[conf.image_bed](conf=conf).__str__(),
                    BackgroundColor.DARK_GRAY,
                    ForegroundColor.WHITE,
                ),
                code=conf.image_bed,
            )

    def print_item(symbol, color, idx):
        ib = IMAGE_BEDS[ImageBedCode(idx)](conf=conf)
        click.echo(f"""{colorize(" " + symbol, color)} {idx} {ib}: {ib.description}""")

    for i in ImageBedCode:
        if auth_data.get(i):
            print_item(chr(10003), ForegroundColor.GREEN, i)
        else:
            print_item(chr(10007), ForegroundColor.RED, i)

    return 0


def run_main():
    sys.exit(cli())


if __name__ == "__main__":
    run_main()
