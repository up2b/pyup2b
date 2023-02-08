#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author:    thepoy
# @Email:     thepoy@163.com
# @File Name: server.py
# @Created:   2023-02-08 14:18:22
# @Modified:  2023-02-08 17:34:15

import socketserver
import json
import re

from http.server import BaseHTTPRequestHandler
from pathlib import Path
from typing import Any, Dict, Optional
from tests import IMAGES_DIR
from requests_toolbelt.multipart import decoder


filename_ptn = re.compile(rb'filename="(.+?)"')


class Handler(BaseHTTPRequestHandler):
    def set_headers(
        self,
        content_type: str,
        content_length: int,
        others: Optional[Dict[str, Any]] = None,
    ):
        self.send_header("Content-type", content_type)
        self.send_header("Content-Length", str(content_length))

        if others:
            for k, v in others.items():
                self.send_header(k, v if isinstance(v, str) else str(v))

        self.end_headers()

    def do_GET(self):
        path = Path("." + self.path)

        print(path)

        if not path.exists():
            self.send_error(404)

            return

        self.send_response(200)

        self.set_headers("image/png", path.stat().st_size)

        self.wfile.write(path.open("rb").read())

    def do_POST(self):
        length = int(self.headers["content-length"])
        body = self.rfile.read(length)

        content_type = self.headers["Content-Type"]

        part = decoder.MultipartDecoder(body, content_type).parts[0]

        disposition: bytes = part.headers[b"Content-Disposition"]  # type: ignore
        searched = filename_ptn.search(disposition)
        if not searched:
            self.send_error(400)

            return

        filename = searched.group(1).decode()
        filepath = IMAGES_DIR / filename

        if not filepath.exists():
            self.send_error(400)

            return

        if filepath.stat().st_size != len(part.content):
            self.send_error(400, "upload failed")

            return

        resp = {
            "status": "ok",
            "url": "http://localhost:8000/images/" + filename,
        }

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(resp).encode())
        return


def run_server():
    PORT = 8000

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("serving at port", PORT)
        httpd.serve_forever()


if __name__ == "__main__":
    run_server()
