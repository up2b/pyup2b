[简体中文](https://github.com/thep0y/up2b/blob/main/README.zh_CN.md)

# UP2B

A package that can upload images to the image bed in the terminal.

It supports **windows**, **linux** and **macOS** system. 

# Features

Support the automatic upload of pictures of the following image bed:

- sm.ms
- imgse.com -> imgtu.com
- github.com

Support automatic compression of `jpeg/jpg` and `png` format images.

# How to use

Install the package:

```shell
pip install up2b
```

Usage Options:

```
usage: test.py [-h] [-v] [-aac] [-aw]
               [-c {0: 'sm.ms', 1: 'imgtu.com', 2: 'github.com'} | -l USERNAME PASSWORD | -lg ACCESS_TOKEN USERNAME REPO FOLDER | --config-text-watermark X Y OPACITY TEXT FONT_PATH SIZE | -p IMAGE_PATH | -ps IMAGE_PATH [IMAGE_PATH ...]]

A package that can upload pictures to the image bed in Typora.

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -aac                  allow automatic image compression
  -aw, --add-watermark  whether to add text watermark to the images to be uploaded
  --current             show the image bed in use
  --list                list all configured image beds
  -c {0: 'sm.ms', 1: 'imgse.com', 2: 'github.com'}, --choose-site {0: 'sm.ms', 1: 'imgse.com', 2: 'github.com'}
                        choose the image bed you want to use and exit
  -l USERNAME PASSWORD, --login USERNAME PASSWORD
                        save the user authentication token after successful login. You must enter the username and password after `-l` or `--login`
  -lg ACCESS_TOKEN USERNAME REPO FOLDER, --login-git ACCESS_TOKEN USERNAME REPO FOLDER
                        save the authentication information of the git website, such as github
  --config-text-watermark X Y OPACITY TEXT FONT_PATH SIZE
                        configure the text watermark
  -p IMAGE_PATH, --image-path IMAGE_PATH
                        upload only one picture
  -ps IMAGE_PATH [IMAGE_PATH ...], --images-path IMAGE_PATH [IMAGE_PATH ...]
                        upload multiple pictures, the maximum is 10 pictures, use spaces to separate each image path.
```
####  1 Choose image bed

When using for the first time, you must first select a image bed. The available image bed list is after the `-c` parameter of **Options**:

- 0
  - sm.ms
- 1
  - imgse.com
- 2
  - github.com


```shell
# if you want to choose github:
up2b -c 2
```
#### 2 Save authentication information

**General image bed:**

The general picture bed refers to the website that only provides the function of saving images, so **git site** is not included.

When using the general image bed, use `-l` or `--login` to configure authentication information:

```shell
up2b -l username password
```
**Git site:**

Including github.

When using a git site, use `-lg` or `--login-git` to configure authentication information.

The authentication information includes the following four key parameters:

- `ACCESS_TOKEN`
- `USERNAME` 
- `REPO` 
- `FOLDER`
  - If the folder does not exist, it will be created automatically

For example, I want to save the image in the `md` folder in the `image-bed` repository, and enter this command:

```shell
up2b -lg access_token username image-bed md
```

#### 3 (Optional) Write the command in typora

Then fill in the command as shown in the figure below.

There is a parameter `-aac` in the command as an optional parameter, which is used to enable the automatic compression function. 

If this parameter is not added, the image will not be automatically compressed when uploading. If the image size exceeds the limit of the image bed, an exception will be thrown during upload.

Adding this parameter will automatically compress images that exceed the limit size to the limit image size or below, ensuring that images can be uploaded smoothly. 

Turn on automatic compression:

```shell
up2b -aac -ps
```

Turn off automatic compression:

```shell
up2b -ps
```

if you want add a text watermark for each image, you should add `-aw` or `--add-watermark`:

```bash
up2b -aw -ps
```

And you shoud config watermark first, like:

```bash
up2b --config-text-watermark -50 -50 50 'test watermark' '/home/thepoy/.local/share/fonts/simkai.ttf' 48
```
