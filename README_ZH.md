# timg
一个能够自动将 `Typora`中的图片上传到图床的包。

理论上支持linux、macOS和windows，但是macOS上没有进行测试。

![Peek 2021-02-13 13-10](../../../../../../../home/thepoy/Pictures/Peek 2021-02-13 13-10.gif)

# 特点

支持以下图床自动上传:

- sm.ms
- imgchr.com
- gitee.com
- github.com

成功上传到`github`后会返回`jsdelivr`的CDN链接，加快在中国境内对图片的访问速度。

# 怎么用

>  **`Typora` 必须安装！**

安装`timg`包:

```shell
pip install typora-upload-image
```

安装后，会多出一条`timg`命令：

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

#### 选择图床

第一次使用时，必须先选择图床（可选图床列表在`timg -h`里的`-c`参数后面——`[sm,chr,gitee,github]`）：

```shell
timg -c sm
```
#### 保存认证信息

**普通图床**

git仓库本身并不算是图床，所以git仓库之外的图床都是普通图床。

使用普通图床时，用`-l`或`--login`进行认证信息的配置，如：

```shell
timg -l username password
```
**git仓库**

此包所指的git仓库包括`gitee`和`github`，分别针对中国和非中国用户。

使用git仓库作为图床，需要用`-lg`或`--login-git`进行认证信息的配置。

认证信息需要四个参数：

- `ACCESS_TOKEN` 私密令牌
- `USERNAME` 用户名
- `REPO` 仓库名
- `FOLDER` 想要保存在仓库里的哪个文件夹中，会自动创建不存在的文件夹

比如，我想将图片保存在`image-bed`仓库里的`md`文件夹内，输入此命令：

```shell
timg -lg access_token username image-bed md
```

#### 在 typora 内填写命令


然后才能将`timg`命令填到`Typora`里，下面这张图就是自动上传的：

![Typora 2021_2_13 13_41_13](https://gitee.com/thepoy/image-bed/raw/master/md/1613195278517.png)

