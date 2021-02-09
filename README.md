# timg
A module that can upload pictures to the image bed in Typora.

Currently only supports linux system.

# Features

Support the automatic upload of pictures of the following image bed:

- sm.ms

Currently only sm.ms image bed is supported, and other image beds will be considered in the future.

# How to use

>  **Typora must be installed!**

Install the module:

```shell
pip install typora-upload-image
```

Usage Options:

```shell
usage: timg [-h] [-v]
            [--login LOGIN LOGIN | --image-path IMAGE_PATH | --images-path IMAGES_PATH [IMAGES_PATH ...]]

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  --login LOGIN LOGIN, -l LOGIN LOGIN
                        Save the user authentication token after successful login. You
                        must enter the username and password after `-l` or `--login`,
                        such as "timg -l username password"
  --image-path IMAGE_PATH, -p IMAGE_PATH
                        Upload only one picture.
  --images-path IMAGES_PATH [IMAGES_PATH ...], -ps IMAGES_PATH [IMAGES_PATH ...]
                        Upload multiple pictures, the maximum is 10 pictures. Use spaces
                        to separate each image path.
```

Configure in typora:

![1612796753](https://i.loli.net/2021/02/08/MvPFe3U8WXgKtNb.png)

# End

Now, when you add a picture to typora, it will be automatically uploaded to the picture bed.
