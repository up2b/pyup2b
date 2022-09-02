[English](https://github.com/thep0y/up2b)

[电报群](https://t.me/py_up2b)

> 命令行管理太麻烦？试试[up2b-gui](https://github.com/thep0y/up2b-gui)吧！

# up2b

一个能在终端中将图片上传到图床的包。

支持linux、macOS和windows。

## 特点

支持以下图床自动上传:

- ~~sm.ms~~
- ~~imgtu.com~~
- github.com
- ~~coding.net~~

> 上述有删除线的图床都代表**已凉**，已凉的可能性有两种，一是不可达（被和谐），一是反盗链（访问原文件需登录认证）。

成功上传到`github`后会返回`jsdelivr`的CDN链接，加快在中国境内对图片的访问速度。

支持jpeg/jpg和png图片的自动压缩，但仅在测试阶段，可能有些小问题，如果你不想在使用此功能时出现错误或达不到预期则不建议使用。

## 怎么用

安装`up2b`包:

```shell
pip install up2b
```

安装后，会多出一条`up2b`命令：

```
usage: up2b [-h] [-v] [-aac] [-aw] [--current] [--list]
            [-c {0: 'sm.ms', 1: 'imgtu.com', 2: 'github.com', 3: 'coding.net'} | -l USERNAME PASSWORD | -lg ACCESS_TOKEN USERNAME REPO FOLDER | --config-text-watermark X Y OPACITY TEXT FONT_PATH SIZE | -p IMAGE_PATH | -ps IMAGE_PATH [IMAGE_PATH ...]]

一个能将本地图片压缩、加水印或原图上传到图床的包

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -aac                  允许自动压缩图片。开启此项后，超过图床限制大小的图片将会自动压缩到限制大小后再上传
  -aw, --add-watermark  对要上传的图片添加文字水印
  --current             显示正在使用的图床
  --list                列出所有已配置的图床
  -c {0: 'sm.ms', 1: 'imgtu.com', 2: 'github.com', 3: 'coding.net'}, --choose-site {0: 'sm.ms', 1: 'imgtu.com', 2: 'github.com', 3: 'coding.net'}
                        选择要使用的图床
  -l USERNAME PASSWORD, --login USERNAME PASSWORD
                        保存认证信息。你需要在`-l`或`--login`后输入账名和密码
  -lg ACCESS_TOKEN USERNAME REPO FOLDER, --login-git ACCESS_TOKEN USERNAME REPO FOLDER
                        保存 git 类型图床的认证信息，如github
  -lc ACCESS_TOKEN USERNAME PROJECT REPO FOLDER, --login-coding ACCESS_TOKEN USERNAME PROJECT REPO FOLDER
                        保存 Coding 的认证信息
  --config-text-watermark X Y OPACITY TEXT FONT_PATH SIZE
                        配置要添加的文字水印
  -p IMAGE_PATH, --image-path IMAGE_PATH
                        上传一张图片
  -ps IMAGE_PATH [IMAGE_PATH ...], --images-path IMAGE_PATH [IMAGE_PATH ...]
                        上传多张图片。多张图片路径之间以空格分隔，最多能上传 10 张
```

### 1 选择图床

第一次使用时，必须先选择图床。

`up2b`的`-c`参数可选值为：

- 0
  - sm.ms
- 1
  - imgtu.com
- 2
  - github.com
- 3
  - coding.net


```shell
# 如果你想选择sm.ms
up2b -c 0
```
### 2 保存认证信息

#### **普通图床：**

git仓库本身并不算是图床，所以git仓库之外的图床都是普通图床。

使用普通图床时，用`-l`或`--login`进行认证信息的配置，如：

```shell
up2b -l username password
```
#### **git仓库：**

此包所指的git仓库包括`github`。

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

### 3 (可选) 在 typora 内填写命令

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

## TODO

鉴于图床网站凉的速度超乎想象，所以我不打算再对任何图床进行支持，下个大版本中将使用配置文件的方式由用户自行添加图床，并添加检测图床可用性的功能。

以下是 v1 版本的初步功能设计。

- [ ] 设计通用配置文件规则

  - [ ] 图床类型
    - [ ] git
    - [ ] api
    - [ ] 非api

- [ ] 图床可用性检测及无效标记

  - [ ] 对配置文件中的图床进行可达（超时）检测
  - [ ] 对不可达（超时）的图床添加一个无效标记，并记录检测时间
  - [ ] 用户可设置检测周期，在检测周期内不会检测无效图床以节约时间
  - [ ] 用户可设置删除（软删除）无效图床配置的周期次数，当达到或超过此次数的检测周期后，将在配置文件中将此图床标记为永久失效（软删除）
  - [ ] 用户可在配置文件中删除无效标记

- [ ] 本地网页配置

  配置文件规则复杂，为了降低用户的使用成本，为用户提供网页版可视化配置项。

  - [ ] 可配置规则
  - [ ] 可检测可用性
  - [ ] 可设置无效性检测周期
  - [ ] 可手动添加、删除无效标记

v1 版本后将不再维护 up2b-gui 项目，将可视化配置转移动网页配置中。

除以上功能外，仍需考虑的点有：

- 技术栈的选择

  python 虽然简单，但是为了更好地支持网页配置和降低前后端维护成本，我也在考虑 node 实现。

  同时，使用图床的人中有一些普通用户，既不懂 node，也不懂 python，这种情况下需要使用可编译语言发布二进制可执行文件，所以 Go 也在考虑的范围内。当前我正在接触 rust，也不排除用 rust 实现。

- 配置文件的类型

  当前的配置文件是 json，如果一旦规则复杂起来，json 可能就不太适合作为可编辑的配置文件了，故需在 yaml 和 toml 中作出选择。
