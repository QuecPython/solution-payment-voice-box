# QuecPython 云喇叭解决方案

中文 | [English](readme.md)

欢迎来到 QuecPython 云喇叭解决方案仓库！本仓库提供了一个全面的解决方案，用于使用 QuecPython 开发云喇叭设备应用程序。

## 目录

- [介绍](#介绍)
- [功能](#功能)
- [快速开始](#快速开始)
  - [先决条件](#先决条件)
  - [安装](#安装)
  - [运行应用程序](#运行应用程序)
- [目录结构](#目录结构)
- [用法](#用法)
- [贡献](#贡献)
- [许可证](#许可证)
- [支持](#支持)

## 介绍

QuecPython推出的云喇叭解决方案主要针对移动支付行业，包括支付收款、实时播报功能，并且可自定义语音播放（广告、特色语音等），支持历史订单回播，支持断码屏显示，用户可基于此方案进行二次开发。


## 功能

- **语音播报**：支持多种格式语音文件
- **屏幕显示**：支持断码屏显示交易金额、时间、状态等
- **订单管理**：支持历史订单回看、回播
- **多协议支持**：MQTT、TCP、HTTP
- **超长待机**：支持超低功耗模式
- **远程升级**：支持 OTA 远程更新语音文件

## 快速开始

### 先决条件

在开始之前，请确保您具备以下先决条件

- 硬件
  - 一块 [QuecPython EC600U 开发板](https://python.quectel.com/doc/Getting_started/zh/evb/ec600x-evb.html) 、一个喇叭
  - USB 数据线（USB-A 转 USB-C）
  - 电脑（Windows 7、Windows 10 或 Windows 11）
- 软件
  - QuecPython 模块的 USB 驱动
  - QPYcom 调试工具
  - QuecPython 固件及相关软件资源
  - Python 文本编辑器（例如，[VSCode](https://code.visualstudio.com/)、[Pycharm](https://www.jetbrains.com/pycharm/download/)）

### 安装

1. **克隆仓库**：

   ```
   git clone https://github.com/QuecPython/solution-payment-voice-box.git
   cd solution-payment-voice-box
   ```

2. **烧录固件**： 按照[说明](https://python.quectel.com/doc/Application_guide/zh/dev-tools/QPYcom/qpycom-dw.html#Download-Firmware)将固件烧录到开发板上。**注意根据开发板类型选择对应的固件**

### 运行应用程序

1. **连接硬件**：

   - 使用 USB 数据线将开发板连接到计算机的 USB 端口。

2. **将代码下载到设备**：

   - 启动 QPYcom 调试工具。
   - 将数据线连接到计算机。
   - 按下开发板上的 **PWRKEY** 按钮启动设备。
   - 按照[说明](https://python.quectel.com/doc/Application_guide/zh/dev-tools/QPYcom/qpycom-dw.html#Download-Script)将 `code` 文件夹中的所有文件导入到模块的文件系统中，保留目录结构。

3. **运行应用程序**：

   - 选择 `File` 选项卡。
   - 选择 `_main.py` 脚本。
   - 右键单击并选择 `Run` 或使用`运行`快捷按钮执行脚本。
   

## 目录结构

```
solution-payment-voice-box/
├── code/
│   ├── _main.py                       # 程序入口文件
│   ├── audio_control.py               # 音频播放相关代码
│   ├── audio_file/                    # 音频文件
│   │   ├── anjianyin.mp3
│   │   ├── audio.bin
│   │   ├── chongdianyiwancheng.mp3
│   │   ├── chongdianyiyichu.mp3
│   │   ├── ...mp3
│   │   └── zhengzaiguanji.mp3
│   ├── button_control.py              # 按键控制相关代码
│   ├── cloud.py                       # 连接云平台相关代码（MQTT、HTTP等）
│   ├── common.py                      # 日志、配置文件读取保存相关代码
│   ├── conf_store.json                # 程序运行必要参数配置等（静态）
│   ├── const.py                       # 程序运行必要参数配置等
│   ├── EventMesh.py                   # 事件管理相关代码
│   ├── lcd_control.py                 # 断码屏/LCD屏控制代码
│   ├── led_control.py                 # LED灯控制代码
│   ├── mgr.py                         # 充电管理、设备信息管理、历史订单、远程控制等
│   ├── ota_control.py                 # ota升级相关代码
│   └── utils/                         # 加密相关代码
│       ├── hashlib.py
│       └── hmac.py
├── doc/
│   ├── en/                            # 用户指导文档英文版
│   │   ├── media/
│   │   │   ├── cloudspeaker_1.png
│   │   │   ├── cloudspeaker_10.png
│   │   │   ├── ...png
│   │   │   └── cloudspeaker_9.png
│   │   └── User-Guide.md
│   └── zh/                            # 用户指导文档中文版
│       ├── media/
│       │   ├── cloudspeaker_1.png
│       │   ├── cloudspeaker_10.png
│       │   ├── ...png
│       │   └── cloudspeaker_9.png
│       └── 应用指导.md
├── LICENSE
├── readme.md
└── readme_zh.md
```

## 用法

点此查看[用户指导文档](./docs/zh/应用指导.md)。

## 贡献

我们欢迎对本项目的改进做出贡献！请按照以下步骤进行贡献：

1. Fork 此仓库。
2. 创建一个新分支（`git checkout -b feature/your-feature`）。
3. 提交您的更改（`git commit -m 'Add your feature'`）。
4. 推送到分支（`git push origin feature/your-feature`）。
5. 打开一个 Pull Request。

## 许可证

本项目使用 Apache 许可证。详细信息请参阅 [LICENSE](LICENSE) 文件。

## 支持

如果您有任何问题或需要支持，请参阅 [QuecPython 文档](https://python.quectel.com/doc) 或在本仓库中打开一个 issue。