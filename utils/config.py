import tomllib
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger as lg

# Setup paths
ROOT = Path(__file__).resolve().parents[1]
TOML_PATH = ROOT / "config.toml"
ENV_PATH = ROOT / ".env"
lg.info(f"--- Loading .env and config.toml from {ROOT} ---")

# Load .env file
load_dotenv(ENV_PATH)
lg.success("Loaded .env")

# Load config.toml
config_toml = {}
with open(TOML_PATH, "rb") as f:
    config_toml = tomllib.load(f)
lg.success("Loaded config.toml")


# helper function to get config values
def _get(section: str, key: str, cast=str):
    try:
        return cast(config_toml[section][key])
    except KeyError:
        raise KeyError(f"缺少配置: [{section}] {key}")
    except Exception as e:
        raise ValueError(f"配置类型错误: [{section}] {key} -> {e}")


# --- Configuration CONSTANTS from config.toml ---
# SERVER
SERVER_PORT = _get("SERVER", "SERVER_PORT", int)

# CACHE_PATHS
CACHE_ROOT = _get("CACHE_PATHS", "CACHE_ROOT", str)
FASTER_WHISPER_MODEL_FOLDER = str(
    Path(CACHE_ROOT) / _get("CACHE_PATHS", "FASTER_WHISPER_MODEL_FOLDER", str)
)
OPENWAKEWORD_MODEL_FOLDER = str(
    Path(CACHE_ROOT) / _get("CACHE_PATHS", "OPENWAKEWORD_MODEL_FOLDER", str)
)

# LLM
LLM_BASE_URL = _get("LLM", "LLM_BASE_URL", str)

# TTS
TTS_API_URL = _get("TTS", "TTS_API_URL", str)
TTS_REF_AUDIO_PATH = _get("TTS", "TTS_REF_AUDIO_PATH", str)
TTS_PROMPT_TEXT = _get("TTS", "TTS_PROMPT_TEXT", str)
TTS_PROMPT_LANG = _get("TTS", "TTS_PROMPT_LANG", str)

# STT
STT_MODEL_SIZE = _get("STT", "STT_MODEL_SIZE", str)
STT_COMPUTE_TYPE = _get("STT", "STT_COMPUTE_TYPE", str)
