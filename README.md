# Talos: AI Voice Assistant with Wake Word and LLM Support

<div align="center">

[![Version](https://img.shields.io/badge/version-0.1.0-blue)](https://github.com/SiriusAhu/Talos-Voice-Assistant/releases) [![Python](https://img.shields.io/badge/python-3.12.11-blue?logo=python)](https://www.python.org/downloads/release/python-31211/)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

[![OpenWakeWord](https://img.shields.io/badge/OpenWakeWord-onnx-orange?logo=sound)](https://github.com/dscripka/openWakeWord)
[![Faster-Whisper](https://img.shields.io/badge/Faster--Whisper-ASR-green?logo=whisper)](https://github.com/SYSTRAN/faster-whisper)
[![GPT-SoVITS](https://img.shields.io/badge/GPT--SoVITS-TTS-purple?logo=ai)](https://github.com/RVC-Boss/GPT-SoVITS)

</div>

<div align="center">

[中文](README_zh.md) | [English](README.md)

</div>

---

**Talos** is an AI voice assistant that integrates **wake word detection**, **speech recognition**, **LLM interaction**, and **text-to-speech synthesis**.

---

## Features

* 🎤 **Wake Word Detection**: Offline wake word recognition powered by `openwakeword`
* 🗣️ **Speech Recognition**: Accurate speech-to-text using `faster-whisper`
* 🤖 **LLM Integration**: Supports OpenAI-compatible APIs (e.g., DeepSeek)
* 🔊 **Text-to-Speech**: High-quality speech synthesis via `GPT-SoVITS API v2`
* ⚡ **Real-time Streaming**: Stream responses and audio playback
* 🎯 **Modular Design**: Decoupled services for easy extension and maintenance

---

## Tech Stack

* **Python 3.12+** — Core programming language
* **FastAPI** — Web service framework
* **OpenWakeWord** — Wake word detection engine
* **Faster-Whisper** — Speech recognition model
* **GPT-SoVITS** — Text-to-speech engine
* **uv** — Modern Python package manager

---

## Quick Start

### Requirements

* Python 3.12+ (tested on 3.12.11)
* CUDA-enabled GPU (recommended, CPU also supported)
* Microphone and speakers

### Installation

1. **Clone the repo**

   ```bash
   git clone https://github.com/SiriusAhu/Talos-Voice-Assistant
   cd Talos-Voice-Assistant
   ```

2. **Install dependencies**

   > Recommended: use `uv`.
   > A `requirements.txt` (generated via `uv pip freeze`) is also provided for compatibility with other package managers.

   Using `uv`:

   ```bash
   uv sync
   ```

   Using pip:

   ```bash
   pip install -r requirements.txt
   ```

3. **Wake word model**

   > Automated setup

   Talos provides a pre-trained wake word model (`Hi Talos`) at
   `provided_models/openwakeword/hi_talos.onnx`.

   On first run, `server/listener_service.py` will automatically copy it to `.cache/openwakeword/hi_talos.onnx`.
   (Model size < 1MB, so the copy is lightweight.)

   To add your own wake word model, simply place the `.onnx` file into `provided_models/openwakeword/` and adjust the configuration (to be implemented).

4. **Configure environment**

   ```bash
   cp config.toml.example config.toml
   cp .env.example .env
   ```

5. **Run services**

   > Two terminals are required:

   **Windows**

   ```bash
   ./run_main_server.bat        # start main server
   ./run_listener_service.bat   # start listener service
   ```

   **Linux**

   ```bash
   ./run_main_server.sh
   ./run_listener_service.sh
   ```

   * **`listener_service.py`** — handles wake word detection (OpenWakeWord) and speech recognition (Faster-Whisper)
   * **`main_server.py`** — handles LLM interaction, text-to-speech requests, and streaming audio output

---

## License

This project is licensed under [GPL v3](https://www.gnu.org/licenses/gpl-3.0).
Any modifications or redistributed versions must also remain open source.

---

## Roadmap

* [ ] Support additional TTS engines (e.g., `IndexTTS/IndexTTS2`)
* [ ] Multi-language support and localization
* [ ] Configurable system prompts and role settings (`config/roles/Chara1.toml`)
* [ ] Automated download and management of OpenWakeWord models
* [ ] Dynamic adaptation of recording length
* [ ] Web-based management interface
* [ ] Docker container deployment (long-term goal)

---

## ⚠️ Notes

1. Current TTS is only compatible with [GPT-SoVITS API v2](https://github.com/RVC-Boss/GPT-SoVITS/blob/main/api_v2.py)
2. On first run, the `faster-whisper` model will be downloaded to `.cache/faster-whisper` — please ensure network access

---

## Acknowledgements

Talos is built on top of the following excellent open-source projects — heartfelt thanks to their authors:

* [OpenWakeWord](https://github.com/dscripka/openWakeWord) — Efficient offline wake word detection
* [Faster-Whisper](https://github.com/SYSTRAN/faster-whisper) — Lightweight and accurate speech recognition
* [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS) — High-quality text-to-speech synthesis
