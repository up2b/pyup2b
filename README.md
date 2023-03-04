[English](https://github.com/thep0y/up2b)

> 命令行管理太麻烦？试试[up2b-gui](https://github.com/thep0y/up2b-gui)吧！

<h1 align="center">UP2B</h1>

<p align="center">
	<a href="https://pepy.tech/project/up2b"><img alt="Downloads" src="https://static.pepy.tech/badge/up2b"></a>
</p>

一个能在终端中将图片上传到图床的包。

支持 Linux、macOS 和 Windows。

## 特点

支持以下图床自动上传:

- sm.ms
- imgse.com(原imgtu.com)
- github.com
- imgtg.com

成功上传到`github`后会返回`jsdelivr`的CDN链接，加快在中国境内对图片的访问速度。

支持jpeg/jpg和png图片的自动压缩，但仅在测试阶段，可能有些小问题，如果你不想在使用此功能时出现错误或达不到预期则不建议使用。

## 怎么用

安装`up2b`包:

```shell
pip install up2b
```

安装后，会多出一条`up2b`命令：

```
Usage: python -m up2b [OPTIONS] COMMAND [ARGS]...

Options:
	-h, --help     显示本帮助信息
	-v, --version  显示版本信息
Commands:
	choose            选择图床
	config-watermark  配置文字水印
	current           显示正在使用的图床
	list              列出支持的所有图床
	login             保存图床登录信息
	login-git         保存 git 登录信息
	upload            上传图片
```

### 1 选择图床

第一次使用时，必须先选择图床。

`up2b`的`choose`命令的可选值为：

- 0
  - sm.ms
- 1
  - imgse.com
- 2
  - github.com
- 4
  - imgtg.com

```bash
# 如果你想选择sm.ms
up2b choose 0
```
> 你可能也注意到了，图床的 code 不连续，这是因为最初写这个项目的时候没有考虑到一些图床挂掉的可能性，删掉一些挂掉的图床后，为了使配置文件不冲突，所以图床 code 无法连续。
>
> 
>
> 在 1.0 版本中，将不会再使用数字作为图床的 code，这个问题将会解决，同时会启用全新的配置文件，与 0.X.X 版本的配置文件将不通用。

### 2 保存认证信息

#### **普通图床：**

git仓库本身并不算是图床，所以git仓库之外的图床都是普通图床。

使用普通图床时，用`login`命令进行认证信息的配置，如：

```shell
up2b login username password
```
#### **git仓库：**

此包所指的git仓库包括`github`。

使用git仓库作为图床，需要用或`login-git`命令进行认证信息的配置。

认证信息需要四个参数：

- `ACCESS_TOKEN` 私密令牌
- `USERNAME` 用户名
- `REPO` 仓库名
- `FOLDER` 想要保存在仓库里的哪个文件夹中，会自动创建不存在的文件夹

比如，我想将图片保存在`image-bed`仓库里的`md`文件夹内，输入此命令：

```shell
up2b login-git access_token username image-bed md
```

### 3 (可选) 在 typora 内填写命令

最重要的上传功能：

```
Usage: up2b upload [OPTIONS] [IMAGE_PATH]...

	上传图片

Options:
	-aw, --add-watermark  对要上传的图片添加文字水印
	-ac, --auto-compress  允许自动压缩图片
	-ic, --ignore-cache   忽略数据库缓存，强制上传图片
	-h, --help            Show this message and exit.
```



将`up2b upload`命令填到`Typora`里，命令里有个参数`-ac`为可选参数，其作用为开启自动压缩功能，如果不加此参数，上传图片时不会自动压缩，超出图床限制大小就会报错。而添加此参数，则会自动将超限图片压缩到限制图片大小或以下，保证顺利上传。

但自动压缩功能当前没有经过严谨地测试，所以不能保证不出问题，有问题请将异常的截图发在电报群里。

开启自动压缩功能：

```shell
up2b upload -ac
```

不开启自动压缩功能：

```shell
up2b upload
```

你也可以添加文字水印：

```bash
up2b upload -aw
```

但需先配置文字水印的相关信息：

```bash
up2b config-watermark -50 -50 50 'test watermark' '/path/of/font/font.ttf' 48
```

![配置示例](https://s2.loli.net/2023/03/04/wNqgOpn4Tz5ZUHQ.png)

## 自行打包

如果此项目中更新了某些特性对你来说很有用，但尚未发布新的 release，那么你可以自行打包安装。

### 创建虚拟环境

如果你不担心对环境中的其他包产生影响，也不介意自己的 Python 库中多一些可能永远用不到的包，则可以忽略此步。

> 如果你使用的环境管理工具为 pthon 内置的 venv，请自行创建环境，这里不多介绍。

```bash
conda create -n up2b-temp python=3.10
conda activate up2b-temp
```

### 安装依赖

```bash
pip install build
```

### 打包

```bash
python -m build
```

会在项目的根目录创建`dist`目录，里面就有打包好的`whl`文件，安装即可：

```
pip install -U dist/up2b-*-py3-none-any.whl
```

## TODO

鉴于图床网站凉的速度超乎想象，所以在下个大版本中我不打算再对任何图床进行支持，而是使用配置文件的方式由用户自行添加图床，并添加检测图床可用性的功能。

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
