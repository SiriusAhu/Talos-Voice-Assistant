# main_server.py

import os
from typing import Generator

import requests
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from loguru import logger as lg
from openai import OpenAI

from utils import config

# Initialize FastAPI app
app = FastAPI()

# System prompt for the LLM
# TODO: Make this configurable (a config/role folder?)
SYSTEM_PROMPT = """
你是一个经验丰富的香烟销售助手，旨在为用户科普香烟相关知识。
人设：你讨厌芙蓉王但尊重其地位。相比于传统香烟，你更推荐电子烟（考虑到健康等因素），虽然你知道无论哪种烟草制品都对健康有害。在谈论香烟话题时你总是会说明你对芙蓉王和电子烟的看法。

回答必须严格分为三部分：  

1. **极简回应**：用较短的一句话或词复数或承接开头（如“我知道了，你想了解xx”、“说到xx，让我来给你介绍一番”、“嗯，这个问题不错，我也有过研究”）。  
2. **主体回答**：用两句话以内，简洁明了地解释或回答用户问题。  
3. **追问引导**：最后总是加上一句引导，询问用户是否想了解更详细的信息。  

示例：  
用户：什么是烟草？  
助手：说到烟草。烟草是一种含有尼古丁的植物，常用于制造香烟。你想让我给你介绍一下它的历史和常见种类吗？
"""

# Punctuation marks indicating the end of a sentence
SENTENCE_ENDINGS = ["。", "！", "？", "!", "?", ".", "\n"]

# --- 1. Initialize LLM client ---
llm_client = None
try:
    llm_client = OpenAI(api_key=os.getenv("LLM_API_KEY"), base_url=config.LLM_BASE_URL)
    lg.info("LLM client initialized successfully.")
except Exception as e:
    lg.error(f"Error in initializing LLM client: {e}")


# --- 2. Core function to get TTS audio chunk ---
def get_tts_audio_chunk(text_to_speak: str) -> bytes:
    """
    Get TTS audio chunk from GPT-SoVITS server.
    TODO: Add more tts providers and selection logic.
    """
    if not config.TTS_API_URL:
        lg.error("TTS Error: TTS_API_URL is not configured.")
        return b""

    payload = {
        "text": text_to_speak,
        "text_lang": "zh",
        "ref_audio_path": config.TTS_REF_AUDIO_PATH,
        "prompt_text": config.TTS_PROMPT_TEXT,
        "prompt_lang": config.TTS_PROMPT_LANG.lower(),
        "text_split_method": "cut5",
    }

    try:
        response = requests.get(config.TTS_API_URL, params=payload, timeout=60)
        if response.status_code == 200:
            return response.content
        else:
            lg.error(
                f"TTS API Error: Status {response.status_code}, Body: {response.text}"
            )
            return b""
    except requests.exceptions.RequestException as e:
        lg.error(f"TTS request failed: {e}")
        return b""


# --- 3. FastAPI endpoints ---
@app.post("/process-stream")
def process_stream(command_data: dict) -> StreamingResponse:
    """
    Get a text command from the client, send it to the LLM for streaming response,
    convert the response to speech in real-time, and stream the audio back to the client.

    FIXME: Check streaming handling logic.
    """
    query = command_data.get("text", "")
    if not query:
        raise HTTPException(status_code=400, detail="No text provided.")
    if not llm_client:
        raise HTTPException(status_code=503, detail="LLM client is not available.")

    def stream_generator() -> Generator[bytes, None, None]:
        """A generator to handle the full life cycle of the request."""
        lg.info(f"Received query: '{query}'")
        sentence_buffer = ""

        try:
            # 1. Request streaming response from LLM
            llm_stream = llm_client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": query},
                ],
                stream=True,
            )
            lg.info("...Receiving LLM stream...")

            # 2. Iterate over LLM's token stream and concatenate sentences
            for chunk in llm_stream:
                token = chunk.choices[0].delta.content
                if token:
                    sentence_buffer += token
                    if token[-1] in SENTENCE_ENDINGS:
                        # 3. Found complete sentence, immediately perform TTS and stream back
                        sentence = sentence_buffer.strip()
                        lg.info(f"Synthesizing sentence: '{sentence}'")
                        audio_chunk = get_tts_audio_chunk(sentence)
                        if audio_chunk:
                            # 4. Send audio chunk length and data to client
                            yield len(audio_chunk).to_bytes(4, "big")
                            yield audio_chunk
                        sentence_buffer = ""

            # 5. Handle any remaining text fragments at the end of the stream
            if sentence_buffer.strip():
                final_fragment = sentence_buffer.strip()
                lg.info(f"Synthesizing final fragment: '{final_fragment}'")
                audio_chunk = get_tts_audio_chunk(final_fragment)
                if audio_chunk:
                    yield len(audio_chunk).to_bytes(4, "big")
                    yield audio_chunk

            lg.success("LLM stream finished.")

        except Exception as e:
            lg.error(f"An error occurred during stream generation: {e}")
            # TODO: yield a special error signal
        finally:
            lg.info("Stream generator finished.")

    return StreamingResponse(stream_generator(), media_type="application/octet-stream")


# --- Main server entry point ---
if __name__ == "__main__":
    lg.info("Starting EchoStream Assistant Server...")
    uvicorn.run(
        "server.main_server:app", host="127.0.0.1", port=config.SERVER_PORT, reload=True
    )


# TODO:处理空输入
# TODO:处理唤醒词连续触发
