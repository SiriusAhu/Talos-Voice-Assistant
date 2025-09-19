# server/wake_service.py

import io
import queue
import shutil
import threading
from pathlib import Path
from typing import Optional
from warnings import filterwarnings

import numpy as np
import openwakeword
import pyaudio
import requests
import sounddevice as sd
import soundfile as sf
import torch
from faster_whisper import WhisperModel
from loguru import logger as lg

filterwarnings("ignore")  # Filter out annoying warnings from libraries

from utils import config  # Load configuration

# Resolve paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]
OWW_DIR = (
    PROJECT_ROOT / config.OPENWAKEWORD_MODEL_FOLDER
).resolve()  # OWW: openWakeWord
FWS_DIR = (
    PROJECT_ROOT / config.FASTER_WHISPER_MODEL_FOLDER
).resolve()  # FWS: faster-whisper
CACHE_ROOT = (PROJECT_ROOT / config.CACHE_ROOT).resolve()

OWW_MODEL_NAME = (
    "hi_talos.onnx"  # TODO: integrated with config, auto detect wakeword list
)

HELLO_AUDIO = r"audio/default_hello.wav"
HELLO_AUDIO_PATH = (PROJECT_ROOT / HELLO_AUDIO).resolve()

# Default parameters
SAMPLE_RATE = 16_000
RECORD_SECONDS = 5
WAKE_SCORE_TH = 0.5

FASTAPI_APP_SERVER_URL = f"http://127.0.0.1:{config.SERVER_PORT}/process-stream"

# Initialize global queue for audio playback
audio_player_queue: "queue.Queue[Optional[bytes]]" = queue.Queue()


def init_models():
    """Initialize `OpenWakeWord` and `faster-whisper` models."""  # TODO: Add 'Step x'
    lg.info("--- Initializing models ---")

    # openWakeWord
    try:
        lg.info("Initializing openWakeWord...")
        oww_path = OWW_DIR / OWW_MODEL_NAME
        # Check if onnx file exists, if not, copy it from provided_models
        if not oww_path.exists():
            lg.warning(
                f"openwakeword model not found: {oww_path}, copying from provided_models"
            )
            try:
                shutil.copy(
                    PROJECT_ROOT / "provided_models" / "openwakeword" / OWW_MODEL_NAME,
                    oww_path,
                )
            except Exception as e:
                lg.exception(f"Failed to copy wake model: {e}")
                raise
        oww = openwakeword.Model(wakeword_model_paths=[str(oww_path)])
        lg.success(f"openWakeWord initialized: {oww_path.name}")
    except Exception as e:
        lg.exception(f"Failed to init openWakeWord: {e}")
        raise

    # faster-whisper
    try:
        lg.info("Initializing faster-whisper... (This may take a while)")
        if torch.cuda.is_available():
            device = "cuda"
            lg.info("Using GPU.")
        else:
            device = "cpu"
            lg.warning("GPU not available, using CPU.")
        compute_type = config.STT_COMPUTE_TYPE
        FWS_DIR.mkdir(parents=True, exist_ok=True)

        stt_size = config.STT_MODEL_SIZE
        stt = WhisperModel(
            stt_size,
            device=device,
            compute_type=compute_type,
            download_root=str(
                FWS_DIR
            ),  # Set model cache directory (`/.cache/faster-whisper` by default)
        )
        lg.success(f"faster-whisper loaded: '{stt_size}' on {device} ({compute_type})")
    except Exception as e:
        lg.exception(f"Failed to load faster-whisper: {e}")
        raise

    return oww, stt


# region --- Basic Service Functions ---
def record_command() -> np.ndarray:
    """Record audio command after wake word detected."""
    lg.info("...Recording...")
    rec = sd.rec(
        int(RECORD_SECONDS * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32",
    )
    sd.wait()
    lg.info("Recording done.")
    return rec


def transcribe_command(stt_model: WhisperModel, audio: np.ndarray) -> Optional[str]:
    """Transcribe audio to text using faster-whisper."""
    lg.info("Transcribing (stt)...")
    try:
        tmp = CACHE_ROOT / ".tmp_cmd.wav"
        tmp.parent.mkdir(parents=True, exist_ok=True)
        sf.write(tmp, audio, SAMPLE_RATE)
        segments, _ = stt_model.transcribe(str(tmp), beam_size=5)
        text = "".join(seg.text for seg in segments).strip()
        try:
            tmp.unlink()
        except Exception:
            pass
        lg.info(f"STT Output: {text!r}")
        return text or None
    except Exception as e:
        lg.exception(f"Transcription failed: {e}")
        return None


def audio_player_worker():
    """Thread worker to play audio chunks from the queue."""
    lg.debug("Player thread start")
    while True:
        chunk = audio_player_queue.get()
        if chunk is None:
            break
        try:
            audio_data, sr = sf.read(io.BytesIO(chunk))
            sd.play(audio_data, sr)
            sd.wait()
        except Exception as e:
            lg.exception(f"Player error: {e}")
    lg.debug("Player thread end")


def fetch_audio_stream(text: str):
    lg.info(f"Request TTS stream (from GPT-SoVITS): {text!r}")
    try:
        with requests.post(
            FASTAPI_APP_SERVER_URL, json={"text": text}, stream=True, timeout=120
        ) as resp:
            if resp.status_code != 200:
                lg.error(f"Server {resp.status_code}: {resp.text[:200]}")
                return
            stream = resp.raw
            while True:
                length_bytes = stream.read(4)
                if not length_bytes:
                    break
                n = int.from_bytes(length_bytes, "big")
                audio_player_queue.put(stream.read(n))
    except requests.RequestException as e:
        lg.exception(f"Network error: {e}")
    finally:
        audio_player_queue.put(None)


def play_wav_file(path: Path | str):
    """Play local WAV file. (for hello audio)"""
    try:
        data, sr = sf.read(str(path))
        sd.play(data, sr)
        sd.wait()
        lg.success(f"Played welcome audio: {path}")
    except Exception as e:
        lg.exception(f"Failed to play welcome audio: {e}")


def handle_interaction(stt_model: WhisperModel):
    """Handle the full interaction: record, transcribe, fetch TTS, play."""
    audio = record_command()
    text = transcribe_command(stt_model, audio)
    if not text:
        lg.warning("No transcription. Skip.")
        return

    player = threading.Thread(target=audio_player_worker, daemon=True)
    player.start()
    fetch_audio_stream(text)
    player.join()


# endregion


def main():
    """Main loop"""
    try:
        oww, stt_model = init_models()
    except Exception:
        lg.error("Model initialization failed. Exit.")
        return

    pa = pyaudio.PyAudio()  # Initialize PyAudio
    stream = None  # Declare stream variable for cleanup

    try:
        stream = pa.open(
            rate=SAMPLE_RATE,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=1280,
        )
        lg.info("=" * 50)
        lg.success(
            f'Assistant ready. Listening for wake word "{(OWW_DIR / OWW_MODEL_NAME).name.rsplit(".", 1)[0]}"'
        )
        lg.info("=" * 50)

        # Main loop: listen for wake word
        while True:
            pcm = stream.read(1280, exception_on_overflow=False)
            audio_i16 = np.frombuffer(pcm, dtype=np.int16)
            scores = oww.predict(audio_i16)

            if any(score > WAKE_SCORE_TH for score in scores.values()):
                lg.success("Wake word detected!")
                play_wav_file(HELLO_AUDIO_PATH)  # Play hello audio first
                handle_interaction(stt_model)
                lg.debug("=" * 50)
                lg.success("Ready again. Waiting wake word...")
                lg.debug("=" * 50)

    except KeyboardInterrupt:
        lg.info("Shutdown signal received.")
    except Exception as e:
        lg.exception(f"Unexpected error: {e}")
    finally:
        lg.info("Cleaning up...")
        try:
            if stream:
                stream.close()
        finally:
            pa.terminate()
        audio_player_queue.put(None)
        lg.info("Cleanup complete. Bye.")


if __name__ == "__main__":
    main()
