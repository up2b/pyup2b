[English](https://github.com/thep0y/up2b)

[电报群](https://t.me/py_up2b)

> 命令行管理太麻烦？试试[up2b-gui](https://github.com/thep0y/up2b-gui)吧！

# up2b

一个能够自动将 `Typora`中的图片上传到图床的包。

支持linux、macOS和windows。

![Peek 2021-02-13 13-10](https://cdn.jsdelivr.net/gh/thep0y/image-bed/md/1613400034436.png)

# 特点

支持以下图床自动上传:

- sm.ms
- imgtu.com(原域名imgchr.com)
- gitee.com
- github.com

成功上传到`github`后会返回`jsdelivr`的CDN链接，加快在中国境内对图片的访问速度。

支持jpeg/jpg和png图片的自动压缩，但仅在测试阶段，可能有些小问题，如果你不想在使用此功能时出现错误或达不到预期则不建议使用。

# 怎么用

>  **`Typora` 必须安装！**



安装`up2b`包:

```shell
pip install up2b
```

安装后，会多出一条`up2b`命令：

```
usage: up2b [-h] [-v] [-aac] [-aw] [--current] [--list]
            [-c {0: 'sm.ms', 1: 'imgtu.com', 2: 'gitee.com', 3: 'github.com'} | -l USERNAME PASSWORD | -lg ACCESS_TOKEN USERNAME REPO FOLDER | --config-text-watermark X Y OPACITY TEXT FONT_PATH SIZE | -p IMAGE_PATH | -ps IMAGE_PATH [IMAGE_PATH ...]]

一个能将本地图片压缩、加水印或原图上传到图床的包

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -aac                  允许自动压缩图片。开启此项后，超过图床限制大小的图片将会自动压缩到限制大小后再上传
  -aw, --add-watermark  对要上传的图片添加文字水印
  --current             显示正在使用的图床
  --list                列出所有已配置的图床
  -c {0: 'sm.ms', 1: 'imgtu.com', 2: 'gitee.com', 3: 'github.com'}, --choose-site {0: 'sm.ms', 1: 'imgtu.com', 2: 'gitee.com', 3: 'github.com'}
                        选择要使用的图床
  -l USERNAME PASSWORD, --login USERNAME PASSWORD
                        保存认证信息。你需要在`-l`或`--login`后输入账名和密码
  -lg ACCESS_TOKEN USERNAME REPO FOLDER, --login-git ACCESS_TOKEN USERNAME REPO FOLDER
                        保存 git 类型图床的认证信息，如github、gitee
  --config-text-watermark X Y OPACITY TEXT FONT_PATH SIZE
                        配置要添加的文字水印
  -p IMAGE_PATH, --image-path IMAGE_PATH
                        上传一张图片
  -ps IMAGE_PATH [IMAGE_PATH ...], --images-path IMAGE_PATH [IMAGE_PATH ...]
                        上传多张图片。多张图片路径之间以空格分隔，最多能上传 10 张
```

#### 1 选择图床

第一次使用时，必须先选择图床。

`up2b`的`-c`参数可选值为：

- 0
  - sm.ms
- 1
  - imgtu.com
- 2
  - gitee.com
- 3
  - github.com

```shell
# 如果你想选择sm.ms
up2b -c 0
```
#### 2 保存认证信息

**普通图床：**

git仓库本身并不算是图床，所以git仓库之外的图床都是普通图床。

使用普通图床时，用`-l`或`--login`进行认证信息的配置，如：

```shell
up2b -l username password
```
**git仓库：**

此包所指的git仓库包括`gitee`和`github`，分别针对中国和全球用户（包括中国）。

使用git仓库作为图床，需要用`-lg`或`--login-git`进行认证信息的配置。

认证信息需要四个参数：

- `ACCESS_TOKEN` 私密令牌
- `USERNAME` 用户名
- `REPO` 仓库名
- `FOLDER` 想要保存在仓库里的哪个文件夹中，会自动创建不存在的文件夹

比如，我想将图片保存在`image-bed`仓库里的`md`文件夹内，输入此命令：

```shell
up2b -lg access_token username image-bed md
```

#### 3 在 typora 内填写命令

然后才能将`up2b`命令填到`Typora`里，命令里有个参数`-aac`为可选参数，其作用为开启自动压缩功能，如果不加此参数，上传图片时不会自动压缩，超出图床限制大小就会报错。而添加此参数，则会自动将超限图片压缩到限制图片大小或以下，保证顺利上传。

但自动压缩功能当前没有经过严谨地测试，所以不能保证不出问题，有问题请将异常的截图发在电报群里。

开启自动压缩功能：

```shell
up2b -aac -ps
```

不开启自动压缩功能：

```shell
up2b -ps
```

你也可以添加文字水印：

```bash
up2b -aw -ps
```

但需先配置文字水印的相关信息：

```bash
up2b --config-text-watermark -50 -50 50 'test watermark' '/home/thepoy/.local/share/fonts/simkai.ttf' 48
```

下面这张图就是自动上传的：

![截屏2021-04-03 10.52.12](https://cdn.jsdelivr.net/gh/thep0y/image-bed/md/1620902616449.png)

macOS 系统中，因环境变量原因，typora无法调用user下的bin中的命令，需要使用`where up2b`查找`up2b`命令的具体位置，用绝对路径填写。如下图：

![截屏2021-04-03 11.00.22](https://cdn.jsdelivr.net/gh/thep0y/image-bed/md/1620902667868.png)

将 github 个人主页作为水印添加到图片中的效果：

![2022-01-08_00-24](https://cdn.jsdelivr.net/gh/thep0y/image-bed/md/1641573280046.jpg)