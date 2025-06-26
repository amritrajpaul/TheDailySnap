import requests
import openai
from pydub import AudioSegment
from . import config

if config.OPENAI_KEY:
    openai.api_key = config.OPENAI_KEY


def generate_audio(text: str, path: str) -> None:
    """Generate audio for given text and save to path."""
    if config.USE_ELEVENLABS:
        config.logger.info(f"TTS (ElevenLabs {config.ELEVENLABS_VOICE_ID}): {text[:30]}…")
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{config.ELEVENLABS_VOICE_ID}/stream"
        headers = {"xi-api-key": config.ELEVENLABS_API_KEY, "Content-Type": "application/json"}
        payload = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0,
                "use_speaker_boost": True,
            },
        }
        resp = config.with_retry(requests.post, url, headers=headers, json=payload, stream=True)
        if not resp.ok:
            raise RuntimeError(f"ElevenLabs API {resp.status_code}: {resp.text}"[:200])
        with open(path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    else:
        config.logger.info(f"TTS (OpenAI {config.TTS_VOICE}): {text[:30]}…")
        resp = config.with_retry(openai.audio.speech.create, model=config.TTS_MODEL, voice=config.TTS_VOICE, input=text)
        resp.stream_to_file(path)

    seg = AudioSegment.from_file(path)
    seg = seg.speedup(playback_speed=config.SPEEDUP)
    seg.export(path, format="mp3")
    config.logger.info(f"  Audio saved: {path}")

