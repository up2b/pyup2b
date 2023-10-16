#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import sys
import requests
import requests_toolbelt

from typing import Any, Dict, Optional
from tqdm import tqdm


class ProgressBar(tqdm):
    def update_to(self, n: int) -> None:
        self.update(n - self.n)


def upload_with_progress_bar(
    url: str,
    filename: str,
    form: Dict[str, Any],
    headers: Optional[Dict[str, str]] = None,
):
    encoder = requests_toolbelt.MultipartEncoder(form)

    headers = headers or {}

    with ProgressBar(
        total=encoder.len,
        desc=filename,
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

        resp = requests.post(url, data=monitor, headers=headers)

        return resp
