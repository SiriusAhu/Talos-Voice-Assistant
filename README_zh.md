# Talos: 支持唤醒词和LLM的AI语音助手

<div align="center">

<!-- python 3.12 -->
<!-- uv --> 
<!-- GPL v3 -->
[![Python](https://img.shields.io/badge/python-3.12.11-blue?logo=python)](https://www.python.org/downloads/release/python-31211/) 
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv) 
[![GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

[![OpenWakeWord](https://img.shields.io/badge/OpenWakeWord-onnx-orange?logo=sound)](https://github.com/dscripka/openWakeWord)
[![Faster-Whisper](https://img.shields.io/badge/Faster--Whisper-ASR-green?logo=whisper)](https://github.com/SYSTRAN/faster-whisper)
[![GPT-SoVITS](https://img.shields.io/badge/GPT--SoVITS-TTS-purple?logo=ai)](https://github.com/RVC-Boss/GPT-SoVITS)

</div>

<div align="center">

[中文](README_zh.md) | [English](README.md)

</div>


Talos 是一个支持**唤醒词**、**语音识别**、**LLM**与**语音合成**的 AI 语音助手。

---

## 功能特性

- 🎤 **唤醒词检测**: 基于 `openwakeword` 的离线唤醒词识别
- 🗣️ **语音识别**: 使用 `faster-whisper` 进行高精度语音转文本
- 🤖 **大语言模型**: 支持 OpenAI 兼容的 API 接口（如 DeepSeek）
- 🔊 **文本转语音**: 集成 GPT-SoVITS API v2 进行高质量语音合成
- ⚡ **实时流式处理**: 支持流式响应和音频播放
- 🎯 **模块化设计**: 分离的服务架构，易于扩展和维护

## 技术栈

- **Python 3.12+**: 核心开发语言
- **FastAPI**: Web 服务框架
- **OpenWakeWord**: 唤醒词检测引擎
- **Faster-Whisper**: 语音识别模型
- **GPT-SoVITS**: 文本转语音服务
- **UV**: 现代 Python 包管理工具

## 快速开始

### 环境要求

- Python 3.12+ （Talos的开发使用了3.12.11版本）
- CUDA 支持的 GPU（推荐，CPU 也可运行）
- 麦克风和音响设备

### 安装步骤

1. **克隆项目**
    ```bash
    git clone https://github.com/SiriusAhu/Talos-Voice-Assistant
    cd Talos-Voice-Assistant
    ```

2. **安装依赖**
    > 推荐使用`uv`。
    > 项目提供了基于`uv pip freeze`生成的 `requirements.txt`，便于使用其他包管理工具。

    如果你使用`uv`：
    ```bash
    uv sync
    ```

    如果你使用其他包管理工具，请使用`requirements.txt`文件：
    ```bash
    pip install -r requirements.txt
    ```

3. **摆放`openwakeword`唤醒词模型**
    > 已自动化

    项目提供了唤醒词为`Hi Talos`的`onnx`模型，在`provided_models/openwakeword/hi_talos.onnx`目录下。

    第一次运行`server/listener_service.py`时，会自动将其复制到`.cache/openwakeword/hi_talos.onnx`。（考虑到模型体积不足 1MB，首次运行时将自动复制至缓存目录。）

    后续如果想自己添加唤醒词模型，只需要将`onnx`模型放在`provided_models/openwakeword`目录下，然后修改相应配置即可（待实现）

4. **配置环境**
    > 请在复制后根据提示填写`.env`文件和`config.toml`文件：
    ```bash
    # 复制配置文件并修改
    cp config.toml.example config.toml
    
    # 复制环境变量文件并修改
    cp .env.example .env
    ```


5. **运行服务**
    > 需要两个终端来运行不同的服务：

    Windows端：
    ```bash
    ./run_main_server.bat # 启动主服务器
    ./run_listener_service.bat # 启动监听服务（在另一终端运行）
    ```

    Linux端：
    ```bash
    ./run_main_server.sh # 启动主服务器
    ./run_listener_service.sh # 启动监听服务（在另一终端运行）
    ```

    其中
    - `listener_service.py`负责唤醒词检测（`OpenWakeWord`）和语音识别（`Faster-Whisper`）
    - `main_server.py`负责与 LLM 交互、调用 TTS 并返回流式音频

## 许可证

本项目采用 [GPL v3](https://www.gnu.org/licenses/gpl-3.0) 许可证，任何修改或分发的版本必须同样开源。

## 未来计划

- [ ] 支持更多 TTS 引擎（如`IndexTTS/IndexTTS2`）
- [ ] 多语言支持和本地化
- [ ] 可配置的系统提示词和角色设定（`config/roles/Chara1.toml`）
- [ ] 自动下载和管理 OpenWakeWord 模型
- [ ] 语音录音长度自动适配
- [ ] Web 管理界面
- [ ] Docker 容器化部署（长期目标）

## ⚠️注意事项
1. 当前版本的语音生成仅适配 [GPT-SoVITS API v2](https://github.com/RVC-Boss/GPT-SoVITS/blob/main/api_v2.py)
2. 首次运行时会下载`faster-whisper`模型到`.cache/faster-whisper`目录下，请**注意网络环境**

---

## 致谢

项目基于以下优秀的开源项目构建，谨致谢意：

- [OpenWakeWord](https://github.com/dscripka/openWakeWord) —— 高效的离线唤醒词检测
- [Faster-Whisper](https://github.com/SYSTRAN/faster-whisper) —— 轻量且高精度的语音识别
- [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS) —— 高质量的文本转语音生成