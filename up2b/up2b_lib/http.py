#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import sys
import requests
import requests_toolbelt

from typing import Any, Dict, Optional
from tqdm import tqdm
from up2b.up2b_lib.errors import Timeout
from up2b.up2b_lib.file import File


class ProgressBar(tqdm):
    def update_to(self, n: int) -> None:
        self.update(n - self.n)


def upload_with_progress_bar(
    url: str,
    file: File,
    timeout: float,
    form: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
):
    data = form or {}
    data.update(file.to_dict())

    encoder = requests_toolbelt.MultipartEncoder(data)

    headers = headers or {}

    with ProgressBar(
        total=encoder.len,
        desc=file.filename,
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
        miniters=1,
        file=sys.stdout,
    ) as bar:
        monitor = requests_toolbelt.MultipartEncoderMonitor(
            encoder, lambda monitor: bar.update_to(monitor.bytes_read)
        )

        headers.update({"Content-Type": monitor.content_type})

        try:
            resp = requests.post(url, data=monitor, headers=headers, timeout=timeout)
        except requests.exceptions.ReadTimeout:
            raise Timeout("网络连接超时，默认超时时间为 10s，可通过设置环境变量 UP2B_TIMEOUT 修改超时时间")

        return resp
