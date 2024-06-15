# QuecPython Payment Voice Box Solution

[中文](readme_zh.md) | English

Welcome to the Payment Voice Box Solution repository for QuecPython! This repository provides a comprehensive solution for developing payment voice box  applications using QuecPython.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running the Application](#running-the-application)
- [Directory Structure](#directory-structure)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)
- [Support](#support)

## Introduction

The QuecPython Payment Voice Box Solution is primarily designed for the mobile payment industry, including payment collection, real-time broadcast functions, customizable voice playback (advertisements, special voices, etc.), support for historical order playback, and segmented display support. Users can perform secondary development based on this solution.

## Features

- **Voice Broadcast**: Supports various formats of voice files.
- **Screen Display**: Supports segmented display of transaction amounts, time, status, etc.
- **Order Management**: Supports historical order review and playback.
- **Multi-Protocol Support**: MQTT, TCP, HTTP.
- **Long Standby Time**: Supports ultra-low power mode.
- **Remote Upgrade**: Supports OTA remote updates of voice files.

## Getting Started

### Prerequisites

Before you begin, ensure you have the following prerequisites:

- **Hardware**:
  - A [QuecPython EC600U development board](https://python.quectel.com/doc/Getting_started/en/evb/ec600x-evb.html) and a speaker.
  - USB Data Cable (USB-A to USB-C).
  - PC (Windows 7, Windows 10, or Windows 11).

- **Software**:
  - USB driver for the QuecPython module.
  - QPYcom debugging tool.
  - QuecPython firmware and related software resources.
  - Python text editor (e.g., [VSCode](https://code.visualstudio.com/), [Pycharm](https://www.jetbrains.com/pycharm/download/)).

### Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/QuecPython/solution-payment-voice-box.git
   cd solution-payment-voice-box
   ```

2. **Flash the Firmware**: Follow the [instructions](https://python.quectel.com/doc/Application_guide/dev-tools/QPYcom/qpycom-dw.html#Download-Firmware) to flash the firmware to the development board. **Ensure you select the appropriate firmware for your development board type.**

### Running the Application

1. **Connect the Hardware**:

   - Use a USB data cable to connect the development board to the computer's USB port.

2. **Download Code to the Device**:

   - Launch the QPYcom debugging tool.
   - Connect the data cable to the computer.
   - Press the **PWRKEY** button on the development board to start the device.
   - Follow the [instructions](https://python.quectel.com/doc/Application_guide/en/dev-tools/QPYcom/qpycom-dw.html#Download-Script) to import all files within the `code` folder into the module's file system, preserving the directory structure.

3. **Run the Application**:

   - Select the `File` tab.
   - Select the `_main.py` script.
   - Right-click and select `Run` or use the run shortcut button to execute the script.

## Directory Structure

```plaintext
solution-payment-voice-box/
├── code/
│   ├── _main.py                       # Application entry script
│   ├── audio_control.py               # Audio playback related code
│   ├── audio_file/                    # Audio files
│   │   ├── anjianyin.mp3
│   │   ├── audio.bin
│   │   ├── chongdianyiwancheng.mp3
│   │   ├── chongdianyiyichu.mp3
│   │   ├── ...mp3
│   │   └── zhengzaiguanji.mp3
│   ├── button_control.py              # Button control related code
│   ├── cloud.py                       # Cloud platform connection related code (MQTT, HTTP, etc.)
│   ├── common.py                      # Logging, configuration file reading and saving related code
│   ├── conf_store.json                # Static configuration for necessary parameters of the program
│   ├── const.py                       # Necessary parameter configurations for the program
│   ├── EventMesh.py                   # Event management related code
│   ├── lcd_control.py                 # Segment display/LCD screen control code
│   ├── led_control.py                 # LED control code
│   ├── mgr.py                         # Charging management, device information management, historical orders, remote control, etc.
│   ├── ota_control.py                 # OTA upgrade related code
│   └── utils/                         # Encryption related code
│       ├── hashlib.py
│       └── hmac.py
├── doc/
│   ├── en/                            # User guide documentation in English
│   │   ├── media/
│   │   │   ├── cloudspeaker_1.png
│   │   │   ├── cloudspeaker_10.png
│   │   │   ├── ...png
│   │   │   └── cloudspeaker_9.png
│   │   └── User-Guide.md
│   └── zh/                            # User guide documentation in Chinese
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

## Usage

Click here to view the [User Guide](./docs/en/User-Guide.md).

## Contributing

We welcome contributions to improve this project! Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -m 'Add your feature'`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a Pull Request.

## License

This project is licensed under the Apache License. See the [LICENSE](LICENSE) file for details.

## Support

If you have any questions or need support, please refer to the [QuecPython documentation](https://python.quectel.com/doc) or open an issue in this repository.