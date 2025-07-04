import logging
import os
import time
from dotenv import load_dotenv

import json
import tempfile


def getenv_int(name: str, default: int) -> int:
    """Return integer environment variable or default if unset/invalid."""
    try:
        return int(os.getenv(name) or default)
    except ValueError:
        return default


def getenv_float(name: str, default: float) -> float:
    """Return float environment variable or default if unset/invalid."""
    try:
        return float(os.getenv(name) or default)
    except ValueError:
        return default


def getenv_str(name: str, default: str) -> str:
    """Return string environment variable or default if unset/empty."""
    val = os.getenv(name)
    return val if val and val.strip() else default

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

OPENAI_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")

# ---- Provider selection ----
GEN_AI_PROVIDER = getenv_str("GEN_AI_PROVIDER", "openai").lower()
if GEN_AI_PROVIDER == "google" and not GOOGLE_API_KEY:
    GEN_AI_PROVIDER = "openai"

TTS_PROVIDER = os.getenv("TTS_PROVIDER")
if not TTS_PROVIDER:
    TTS_PROVIDER = "elevenlabs" if ELEVENLABS_API_KEY and ELEVENLABS_VOICE_ID else "openai"
TTS_PROVIDER = TTS_PROVIDER.lower()
if TTS_PROVIDER == "elevenlabs" and not (ELEVENLABS_API_KEY and ELEVENLABS_VOICE_ID):
    TTS_PROVIDER = "openai"

USE_ELEVENLABS = TTS_PROVIDER == "elevenlabs"
USE_GOOGLE_TTS = TTS_PROVIDER == "google"

# YouTube credentials from environment
YOUTUBE_CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID")
YOUTUBE_CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET")
YOUTUBE_PROJECT_ID = os.getenv("YOUTUBE_PROJECT_ID")
YOUTUBE_AUTH_URI = os.getenv("YOUTUBE_AUTH_URI")
YOUTUBE_TOKEN_URI = os.getenv("YOUTUBE_TOKEN_URI")
YOUTUBE_AUTH_PROVIDER_X509_CERT_URL = os.getenv("YOUTUBE_AUTH_PROVIDER_X509_CERT_URL")
YOUTUBE_REDIRECT_URIS = os.getenv("YOUTUBE_REDIRECT_URIS")
YOUTUBE_TOKEN_JSON = os.getenv("YOUTUBE_TOKEN_JSON")

# TTS configuration
TTS_MODEL = getenv_str("TTS_MODEL", "tts-1-hd")
TTS_VOICE = getenv_str("TTS_VOICE", "ash")  # sarcastic Indian accent
SPEEDUP = getenv_float("SPEEDUP", 1.1)  # playback speedup

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CLIENT_SECRETS_FILE = os.path.join(tempfile.gettempdir(), "client_secrets.json")
TOKEN_FILE = os.path.join(tempfile.gettempdir(), "token.json")

# Pipeline behaviour
LANGUAGES = [l.strip().lower() for l in getenv_str("VIDEO_LANGUAGES", "en,hi").split(",") if l.strip()]
UPLOAD_TO_YOUTUBE = os.getenv("UPLOAD_TO_YOUTUBE", "1") != "0"


def write_client_secrets() -> None:
    """Create client_secrets.json from environment variables if provided."""
    if YOUTUBE_CLIENT_ID and YOUTUBE_CLIENT_SECRET:
        data = {
            "installed": {
                "client_id": YOUTUBE_CLIENT_ID,
                "client_secret": YOUTUBE_CLIENT_SECRET,
                "project_id": YOUTUBE_PROJECT_ID or "",
                "auth_uri": YOUTUBE_AUTH_URI or "https://accounts.google.com/o/oauth2/auth",
                "token_uri": YOUTUBE_TOKEN_URI or "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": YOUTUBE_AUTH_PROVIDER_X509_CERT_URL or "https://www.googleapis.com/oauth2/v1/certs",
                "redirect_uris": YOUTUBE_REDIRECT_URIS.split(",") if YOUTUBE_REDIRECT_URIS else [
                    "urn:ietf:wg:oauth:2.0:oob",
                    "http://localhost",
                ],
            }
        }
        with open(CLIENT_SECRETS_FILE, "w") as f:
            json.dump(data, f)

MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKGROUND_IMAGE = os.path.join(MODULE_DIR, "..", "assets", "background_fullframe.png")

RSS_SOURCES = {
    "The Hindu (National)": "https://www.thehindu.com/news/national/?service=rss",
    "The Hindu (Business)": "https://www.thehindu.com/business/?service=rss",
    "The Hindu (Sport)": "https://www.thehindu.com/sport/?service=rss",
    "The Hindu (Entertainment)": "https://www.thehindu.com/entertainment/?service=rss",
    "Indian Express (Politics)": "https://indianexpress.com/section/politics/feed/",
    "Indian Express (Business)": "https://indianexpress.com/section/business/feed/",
    "Indian Express (Sports)": "https://indianexpress.com/section/sports/feed/",
    "Indian Express (Tech)": "https://indianexpress.com/section/technology/feed/",
    "Indian Express (Ent)": "https://indianexpress.com/section/entertainment/feed/",
    "Times of India": "https://timesofindia.indiatimes.com/rssfeedstopstories.cms",
    "Hindustan Times": "https://www.hindustantimes.com/feeds/rss/topnews.xml",
    "NDTV (Top Stories)": "https://feeds.feedburner.com/ndtvnews-top-stories",
    "Economic Times": "https://economictimes.indiatimes.com/ETtopstories/rssfeeds/1977021501.cms",
    "Business Standard": "https://www.business-standard.com/rss/latest.xml",
    "LiveMint": "https://www.livemint.com/rss/most-popular",
    "India Today": "https://www.indiatoday.in/rss/home",
    "News18 (India)": "https://www.news18.com/rss/india.xml",
    "Zee News": "https://zeenews.india.com/rss/india-national-news.xml",
    "Reuters (India)": "https://www.reuters.com/places/india/rss",
    "ANI": "https://www.aninews.in/rss/ani-all-news.xml",
    "CNBC TV18": "https://www.cnbctv18.com/rss/rssfeed.xml",
    "Financial Express": "https://www.financialexpress.com/feed/",
    "The Print": "https://theprint.in/feed/",
}
RSS_SOURCES.update({
    "BBC World": "http://feeds.bbci.co.uk/news/world/rss.xml",
    "CNN Top Stories": "http://rss.cnn.com/rss/edition.rss",
    "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml",
    "Reuters World": "https://www.reuters.com/world/rss",
    "The Guardian": "https://www.theguardian.com/world/rss",
})

FEED_LIMIT = getenv_int("FEED_LIMIT", 15)

OUTPUT_DIR = getenv_str("OUTPUT_DIR", "output_v8_global")
FILE_PREFIX = getenv_str("FILE_PREFIX", "news_short_v8_global")
AUDIO_DIR = os.path.join(OUTPUT_DIR, "audio_segments")
HINDI_AUDIO_DIR = os.path.join(OUTPUT_DIR, "audio_segments_hi")
VIDEO_FILE = os.path.join(OUTPUT_DIR, f"{FILE_PREFIX}.mp4")
HINDI_VIDEO_FILE = os.path.join(OUTPUT_DIR, f"{FILE_PREFIX}_hi.mp4")
SUMMARY_FILE = os.path.join(OUTPUT_DIR, "daily_summary.mp4")
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(HINDI_AUDIO_DIR, exist_ok=True)

VIDEO_SIZE = (
    getenv_int("VIDEO_WIDTH", 720),
    getenv_int("VIDEO_HEIGHT", 1280),
)
FONT = getenv_str("FONT", "Arial")
FONT_SIZE = getenv_int("FONT_SIZE", 36)
TEXT_COLOR = getenv_str("TEXT_COLOR", "white")
BG_COLOR = getenv_str("BG_COLOR", "blue")
FPS = getenv_int("FPS", 24)
GOOGLE_TTS_LANGUAGE = getenv_str("GOOGLE_TTS_LANGUAGE", "en-US")

# Retry configuration for API calls
RETRY_LIMIT = getenv_int("RETRY_LIMIT", 3)


def with_retry(func, *args, **kwargs):
    """Execute *func* with retries and exponential backoff."""
    delay = 5
    for attempt in range(RETRY_LIMIT):
        try:
            return func(*args, **kwargs)
        except Exception as exc:
            if attempt == RETRY_LIMIT - 1:
                logger.error(f"{func.__name__} failed after {RETRY_LIMIT} attempts: {exc}")
                raise
            logger.warning(f"{func.__name__} failed ({exc}), retrying...")
            time.sleep(delay)
            delay *= 2

