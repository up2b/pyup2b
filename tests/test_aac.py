#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: thepoy
# @Email: thepoy@aliyun.com
# @File Name: test_aac.py
# @Created: 2021-02-15 08:37:12
# @Modified: 2021-06-18 08:52:36

# import os

# import mimetypes

# from io import BytesIO
# from PIL import Image

# path = "/home/thepoy/Pictures/mac.png"
# raw_size = os.path.getsize(path)
# max_size = 1 * 1024 * 1024


# def main():
#     img_mime, _ = mimetypes.guess_type(path)
#     scale = max_size / raw_size
#     print(scale)
#     img = Image.open(path)
#     width, height = img.size
#     if img_mime == "image/png":
#         img = img.convert("RGB")
#     else:
#         img = img.resize((int(width * scale), int(height * scale)),
#                          Image.ANTIALIAS)
#     img_file = BytesIO()
#     img.save(img_file, "jpeg")
#     # if img_file.tell() > max_size:
#     i = Image.open(img_file)
#     # img.save("test.jpg")


# if __name__ == '__main__':
#     main()