#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author:    thepoy
# @Email:     thepoy@163.com
# @File Name: coding.py
# @Created:   2022-04-01 21:59:20
# @Modified:  2022-04-17 17:19:44

import os
import time
import requests

from base64 import b64encode
from typing import Dict, List, Optional, Union
from functools import cache, cached_property

from up2b.up2b_lib import errors
from up2b.up2b_lib.custom_types import (
    CodingResponse,
    ImageBedType,
    ImageStream,
    ErrorResponse,
    ImageType,
    UploadErrorResponse,
)
from up2b.up2b_lib.up2b_api import Base, ImageBedAbstract
from up2b.up2b_lib.constants import ImageBedCode
from up2b.up2b_lib.utils import check_image_exists, child_logger

logger = child_logger(__name__)


class Coding(Base, ImageBedAbstract):
    folder: str
    token: str
    project: str
    repo: str
    user_id: int
    username: str
    headers: Dict[str, str]

    image_bed_code = ImageBedCode.CODING
    max_size = 20 * 1024 * 1024
    image_bed_type = ImageBedType.common
    api_url = "https://e.coding.net/open-api"

    def __init__(
        self,
        auto_compress: bool = False,
        add_watermark: bool = False,
    ):
        super().__init__(auto_compress, add_watermark)

        self.repo_id = 0

        if self.auth_info:
            self.token = self.auth_info["token"]
            self.repo_id = self.auth_info["repo_id"]
            self.folder = self.auth_info["folder"]
            self.user_id = self.auth_info["user_id"]
            self.username = self.auth_info["username"]
            self.project = self.auth_info["project"]
            self.repo = self.auth_info["repo"]
            self.headers = {
                "Accept": "application/json",
                "Authorization": "token " + self.token,
            }

    def login(
        self, token: str, username: str, project: str, repo: str, folder: str
    ) -> bool:
        self.username = username
        self.token = token
        self.project = project
        self.repo = repo
        project_id = self.__get_project_id()
        repo_id = self.__get_repo_id(project_id)

        config = {
            "token": token,
            "username": username,
            "project": project,
            "project_id": project_id,
            "repo": repo,
            "repo_id": repo_id,
            "folder": folder,
            "user_id": self._get_user_id(),
        }

        self._save_auth_info(config)

        return True

    def _get_user_id(self):
        resp = requests.get(
            f"https://{self.username}.coding.net/api/me", headers=self.headers
        ).json()
        return resp["id"]

    def post(self, data: dict):
        return requests.post(self.api_url, headers=self.headers, json=data).json()

    @cache
    def __get_project_id(self) -> int:
        data = {
            "Action": "DescribeProjectByName",
            "ProjectName": self.project,
        }
        self.headers = {
            "Accept": "application/json",
            "Authorization": "token " + self.token,
        }
        resp = self.post(data)

        return resp["Response"]["Project"]["Id"]

    @cache
    def __get_repo_id(self, project_id: int) -> int:
        data = {
            "Action": "DescribeProjectDepotInfoList",
            "ProjectId": project_id,
        }
        resp = self.post(data)

        for i in resp["Response"]["DepotData"]["Depots"]:
            if i["Name"] == self.repo:
                return i["Id"]

        raise RuntimeError("无法根据项目名和仓库名获取到 repo id")

    @property
    def _last_commit_sha(self) -> str:
        data = {
            "Action": "DescribeGitCommits",
            "DepotId": self.repo_id,
            "PageNumber": 1,
            "PageSize": 1,
            "Ref": "master",
            "Path": "",
            "StartDate": "",
            "EndDate": "",
        }
        resp = self.post(data)
        return resp["Response"]["Commits"][0]["Sha"]

    def _image_url(self, filename: str) -> str:
        return f"https://{self.username}.coding.net/p/{self.project}/d/{self.repo}/git/raw/master/{self.folder}/{filename}?download=false"

    def _upload(self, image: ImageType, message_filename: Optional[str] = None):
        self.check_login()

        image = self._compress_image(image)
        if isinstance(image, str):
            image = self._add_watermark(image)

        suffix = os.path.splitext(str(image))[-1]
        if suffix.lower() == ".apng":
            suffix = ".png"
        filename = f"{int(time.time() * 1000)}{suffix}"

        if isinstance(image, str):
            with open(image, "rb") as fb:
                content = b64encode(fb.read()).decode("utf-8")
        else:
            content = b64encode(image.stream).decode("utf-8")

        data = {
            "Action": "CreateBinaryFiles",
            "DepotId": self.repo_id,
            "LastCommitSha": self._last_commit_sha,
            "Message": f"up2b - {message_filename if message_filename else image}",
            "SrcRef": "master",
            "DestRef": "master",
            "UserId": self.user_id,
            "NewRef": "",
            "GitFiles": [
                {
                    "Path": f"{self.folder}/{filename}",
                    "Content": content,
                    "NewPath": "",
                }
            ],
        }

        resp = self.post(data)
        if "Error" in resp["Response"]:
            return UploadErrorResponse(
                status_code=400,
                error=resp["Response"]["Error"]["Message"],
                image_path=str(image),
            )

        return self._image_url(filename)

    def upload_image(self, image_path: str):
        basename = os.path.basename(image_path)
        logger.debug("uploading: %s", basename)
        return self._upload(image_path, basename)

    def upload_image_stream(self, image: ImageStream):
        logger.debug("uploading: %s", image)
        return self._upload(image)

    def upload_images(
        self, *images: ImageType, to_console=True
    ) -> List[Union[str, UploadErrorResponse]]:
        self.check_login()

        if len(images) > 10:
            raise errors.OverSizeError(
                "You can only upload up to 10 pictures, but you uploaded %d pictures."
                % len(images)
            )

        check_image_exists(*images)

        self._check_images_valid(*images)

        images_url: List[Union[str, UploadErrorResponse]] = []
        for img in images:
            if isinstance(img, str):
                result = self.upload_image(img)
            else:
                result = self.upload_image_stream(img)

            images_url.append(result)

        if to_console:
            for i in images_url:
                print(i)

        self._clear_cache()

        return images_url

    def get_all_images(self):
        data = {
            "Action": "DescribeGitFiles",
            "DepotId": self.repo_id,
            "Ref": "master",
            "Path": self.folder,
        }
        resp = self.post(data)

        images: List[CodingResponse] = []
        for i in resp["Response"]["Items"]:
            images.append(CodingResponse(self._image_url(i["Name"]), i["Name"]))

        return images

    def _delete_image(self, *filenames: str) -> Optional[ErrorResponse]:
        self.check_login()

        data = {
            "Action": "DeleteGitFiles",
            "DepotId": self.repo_id,
            # "Message": "Delete pictures that are no longer used", # 删除的commit消息不是这样
            "Ref": "master",
            "NewRef": "",
            "LastCommitSha": self._last_commit_sha,
            "Paths": [f"{self.folder}/{filename}" for filename in filenames],
        }
        resp = self.post(data)
        if "Error" in resp["Response"]:
            return ErrorResponse(
                status_code=400,
                error=resp["Response"]["Error"]["Message"],
            )

        return None

    def delete_image(
        self,
        filename: str,
    ) -> Optional[ErrorResponse]:
        return self._delete_image(filename)

    def delete_images(
        self,
        filenames: List[str],
    ) -> Optional[ErrorResponse]:
        return self._delete_image(*filenames)

    def __repr__(self):
        return "coding.net"

    @cached_property
    def base_url(self) -> str:
        return "https://%s.coding.net/api" % self.username
