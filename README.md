[简体中文](https://github.com/thep0y/timg/blob/main/README.zh_CN.md)

# timg

A package that can upload pictures to the image bed in `Typora`.

It supports **windows**, **linux** and **macOS** system, but it has not been tested on **macOS** yet. 

![Peek 2021-02-13 13-10](https://cdn.jsdelivr.net/gh/thep0y/image-bed/md/1613195327228.gif)

# Features

Support the automatic upload of pictures of the following image bed:

- sm.ms
- imgchr.com
- gitee.com
- github.com

# How to use

>  **`Typora` must be installed!**

Install the package:

```shell
pip install typora-upload-image
```

Usage Options:

```shell
usage: timg [-h] [-v] [-c {sm,chr,gitee,github} | -l USERNAME PASSWORD | -lg ACCESS_TOKEN USERNAME REPO FOLDER | -p IMAGE_PATH | -ps IMAGE_PATH [IMAGE_PATH ...]]

A package that can upload pictures to the image bed in Typora.

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -c {sm,chr,gitee,github}, --choose-site {sm,chr,gitee,github}
                        choose the image bed you want to use and exit
  -l USERNAME PASSWORD, --login USERNAME PASSWORD
                        save the user authentication token after successful login.
                        You must enter the username and password after `-l` or
                        `--login`
  -lg ACCESS_TOKEN USERNAME REPO FOLDER, --login-git ACCESS_TOKEN USERNAME REPO FOLDER
                        save the authentication information of the git website, such
                        as gitee, github
  -p IMAGE_PATH, --image-path IMAGE_PATH
                        upload only one picture
  -ps IMAGE_PATH [IMAGE_PATH ...], --images-path IMAGE_PATH [IMAGE_PATH ...]
                        upload multiple pictures, the maximum is 10 pictures, use
                        spaces to separate each image path.
```
####  Choose image bed

When using for the first time, you must first select a image bed. The available image bed list is after the `-c` parameter of **Options**:

- sm
- chr
- gitee
- github

```shell
timg -c github
```
#### Save authentication information

**General image bed**

The general picture bed refers to the website that only provides the function of saving images, so **git site** is not included.

When using the general image bed, use `-l` or `--login` to configure authentication information:

```shell
timg -l username password
```
**Git site**

Including gitee and github.

When using a git site, use `-lg` or `--login-git` to configure authentication information.

The authentication information includes the following four key parameters:

- `ACCESS_TOKEN`
- `USERNAME` 
- `REPO` 
- `FOLDER`
  - If the folder does not exist, it will be created automatically

For example, I want to save the image in the `md` folder in the `image-bed` repository, and enter this command:

```shell
timg -lg access_token username image-bed md
```

#### Write the command in typora

Then fill in the command as shown in the figure below.
Configure in `Typora`:

![Typora 2021_2_13 13_40_23](https://cdn.jsdelivr.net/gh/thep0y/image-bed/md/1613195345227.png)

# End

Now, when you add a picture to `Typora`, it will be automatically uploaded to the picture bed.
