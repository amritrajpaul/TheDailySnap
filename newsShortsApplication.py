#!/usr/bin/env python3
"""
news_shorts_v7_john_oliver_smooth.py

v7 variant refined for smooth topic transitions – now with two-stage GPT + embedding
filtering, OpenAI TTS, and aggregated RSS from 20+ Indian media outlets, plus
automated YouTube upload.

1) Phase 1: Semantic filter via embeddings (top 50 of all articles).
2) Phase 2: GPT rates those 50 for newsworthiness (top 20).
3) GPT crafts a ~45-second John Oliver–style script and segments it.
4) OpenAI TTS (model="tts-1-hd", voice="alloy").
5) Sentence-by-segment vertical video (720×1280).
6) Upload to YouTube.
"""


import os
print('Loading API keys from environment variables')

import sys
import json
import logging
import datetime
from typing import List, Dict

import feedparser
import requests
import numpy as np
from dotenv import load_dotenv

import openai
import nltk
from nltk.tokenize import sent_tokenize
from pydub import AudioSegment
from moviepy.editor import (
    TextClip, AudioFileClip,
    concatenate_videoclips, concatenate_audioclips
)

# YouTube API
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
# ---- right after your other imports ----
from moviepy.editor import CompositeVideoClip, ImageClip

# path to the cartoon+black‐panel background
BACKGROUND_IMAGE = "background_fullframe.png"

# ----------- Configuration ------------

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

load_dotenv()
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_KEY:
    logger.error("Missing OPENAI_API_KEY in environment variables.")
    sys.exit(1)
openai.api_key = OPENAI_KEY

# TTS settings
TTS_MODEL = "tts-1-hd"
TTS_VOICE = "onyx"
SPEEDUP   = 1.1  # 10% faster pacing

# YouTube upload settings
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CLIENT_SECRETS_FILE = "client_secrets.json"  # put your OAuth2 client_secret here
TOKEN_FILE = "token.json"

# Aggregated RSS sources (20+ Indian news feeds)
RSS_SOURCES = {
    "The Hindu (National)":     "https://www.thehindu.com/news/national/?service=rss",
    "The Hindu (Business)":     "https://www.thehindu.com/business/?service=rss",
    "The Hindu (Sport)":        "https://www.thehindu.com/sport/?service=rss",
    "The Hindu (Entertainment)": "https://www.thehindu.com/entertainment/?service=rss",
    "Indian Express (Politics)": "https://indianexpress.com/section/politics/feed/",
    "Indian Express (Business)": "https://indianexpress.com/section/business/feed/",
    "Indian Express (Sports)":   "https://indianexpress.com/section/sports/feed/",
    "Indian Express (Tech)":     "https://indianexpress.com/section/technology/feed/",
    "Indian Express (Ent)":      "https://indianexpress.com/section/entertainment/feed/",
    "Times of India":            "https://timesofindia.indiatimes.com/rssfeedstopstories.cms",
    "Hindustan Times":           "https://www.hindustantimes.com/feeds/rss/topnews.xml",
    "NDTV (Top Stories)":        "https://feeds.feedburner.com/ndtvnews-top-stories",
    "Economic Times":            "https://economictimes.indiatimes.com/ETtopstories/rssfeeds/1977021501.cms",
    "Business Standard":         "https://www.business-standard.com/rss/latest.xml",
    "LiveMint":                  "https://www.livemint.com/rss/most-popular",
    "India Today":               "https://www.indiatoday.in/rss/home",
    "News18 (India)":            "https://www.news18.com/rss/india.xml",
    "Zee News":                  "https://zeenews.india.com/rss/india-national-news.xml",
    "Reuters (India)":           "https://www.reuters.com/places/india/rss",
    "ANI":                       "https://www.aninews.in/rss/ani-all-news.xml",
    "CNBC TV18":                 "https://www.cnbctv18.com/rss/rssfeed.xml",
    "Financial Express":         "https://www.financialexpress.com/feed/",
    "The Print":                 "https://theprint.in/feed/"
}

# Output paths
OUTPUT_DIR = "output_v7_smooth"
AUDIO_DIR  = os.path.join(OUTPUT_DIR, "audio_segments")
VIDEO_FILE = os.path.join(OUTPUT_DIR, "news_short_v7_smooth.mp4")
os.makedirs(AUDIO_DIR, exist_ok=True)

# Video settings
VIDEO_SIZE = (720, 1280)
FONT       = "Arial"
FONT_SIZE  = 36
TEXT_COLOR = "white"
BG_COLOR   = "blue"
FPS        = 24

# Ensure NLTK tokenizer is available
nltk.download("punkt", quiet=True)


# ----------- RSS Fetchers ------------

Article = Dict[str, str]

def fetch_rss_feed(url: str, source: str, limit: int = 5) -> List[Article]:
    try:
        feed = feedparser.parse(url)
        entries = feed.entries[:limit]
        arts: List[Article] = []
        for e in entries:
            arts.append({
                "source":    source,
                "title":     e.get("title","").strip(),
                "summary":   (e.get("summary") or e.get("description") or "").strip(),
                "link":      e.get("link","").strip(),
                "published": e.get("published","")
            })
        logger.info(f"    ✓ {len(arts)} from {source}")
        return arts
    except Exception as ex:
        logger.warning(f"    ✖ {source} failed: {ex}")
        return []

def fetch_all(limit_per_feed: int = 5) -> List[Article]:
    logger.info("Step 1: Aggregating RSS feeds")
    all_arts: List[Article] = []
    seen = set()
    for src, url in RSS_SOURCES.items():
        for art in fetch_rss_feed(url, src, limit_per_feed):
            key = art["link"] or art["title"]
            if key and key not in seen:
                seen.add(key)
                all_arts.append(art)
    logger.info(f"Total unique articles fetched: {len(all_arts)}")
    logger.info("Sample articles:")
    for a in all_arts[:5]:
        logger.info(f" → [{a['source']}] {a['title']}")
    return all_arts


# ----------- Phase 1: Embedding Filter ------------

def filter_stage1(articles: List[Article], top_k: int = 50) -> List[Article]:
    logger.info("Phase 1: Semantic filtering via embeddings")
    seed = "India politics commerce sports technology entertainment"
    texts = [seed] + [f"{a['title']} {a['summary']}" for a in articles]
    resp = openai.embeddings.create(model="text-embedding-ada-002", input=texts)
    embs = resp.data
    seed_emb = np.array(embs[0].embedding)
    art_embs = np.array([e.embedding for e in embs[1:]])
    norms = np.linalg.norm(art_embs, axis=1) * np.linalg.norm(seed_emb)
    sims = (art_embs @ seed_emb) / norms
    idxs = np.argsort(-sims)[:top_k]
    filtered = [articles[i] for i in idxs]
    logger.info(f"  Kept top {len(filtered)} articles after embedding filter")
    logger.info("  Sample after Phase 1:")
    for a in filtered[:5]:
        logger.info(f"   • [{a['source']}] {a['title']}")
    return filtered


# ----------- Phase 2: GPT Rating ------------

def filter_stage2(articles: List[Article], top_k: int = 20) -> List[Article]:
    logger.info("Phase 2: GPT rates newsworthiness")
    system = (
        "You are a news editor. Rate each of the following article headlines+summaries "
        "on a scale 1 (least) to 10 (most) for newsworthiness. "
        "Reply in JSON as a list of {\"index\": <i>, \"score\": <0-10>}."
    )
    user = "\n".join(
        f"{i}. {a['title']} — {a['summary']}"
        for i, a in enumerate(articles)
    )
    resp = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"system","content":system},
                  {"role":"user",  "content":user}],
        temperature=0
    )
    try:
        ratings = json.loads(resp.choices[0].message.content)
    except Exception:
        logger.warning("Could not parse ratings JSON, skipping Phase 2")
        return articles[:top_k]
    ratings.sort(key=lambda x: x["score"], reverse=True)
    top_idxs = [r["index"] for r in ratings[:top_k]]
    filtered = [articles[i] for i in top_idxs]
    logger.info(f"  Kept top {len(filtered)} after GPT rating")
    logger.info("  Sample after Phase 2:")
    for a in filtered[:5]:
        logger.info(f"   • [{a['source']}] {a['title']}")
    return filtered


# ----------- GPT Script + Segmentation ------------

def craft_script(articles: List[Article]) -> List[str]:
    """
    1) Write a ~45s John Oliver–style monologue.
    2) Split it into 8–12 coherent segments in JSON["segments"].
    """
    logger.info("Step 3: Crafting & segmenting John Oliver–style script")
    system_prompt = """
You are John Oliver, host of Last Week Tonight. Your mission is to inform citizens with clarity and wit,
never sacrificing factual accuracy or journalistic integrity.

Task:
1) Write one seamless ~45-second monologue covering today's top five pillars: politics, commerce, sports, technology, entertainment.
2) THEN split that monologue into 5–12 coherent segments for short-form video.
Return ONLY valid JSON with a single key "segments" whose value is a list of strings.
""".strip()

    user_msg = "Here are today's pre-filtered articles:\n" + "\n".join(
        f"- [{a['source']}] {a['title']} — {a['summary']}"
        for a in articles
    )
    resp = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"system","content":system_prompt},
                  {"role":"user",  "content":user_msg}],
        temperature=0.7
    )

    content = resp.choices[0].message.content
    try:
        data = json.loads(content)
        segs = data["segments"]
        assert isinstance(segs, list) and all(isinstance(s, str) for s in segs)
        logger.info(f"  ✓ GPT returned {len(segs)} segments")
        return segs
    except Exception as e:
        logger.warning(f"Segmentation JSON parse failed ({e}), falling back to sentences")
        return sent_tokenize(content)


# ----------- TTS & Video ------------

def generate_audio(text: str, path: str):
    logger.info(f"TTS (Ash, sarcastic Indian accent): {text[:30]}…")
    # Prepend a brief direction so 'Ash' knows to use sarcasm + Indian accent + John Oliver style
    resp = openai.audio.speech.create(
        model=TTS_MODEL,
        voice="ash",                        # ← switched to Ash
        input=text                        # ← feed it the styled prompt
    )
    # save raw TTS output
    resp.stream_to_file(path)
    # post-process for pacing
    seg = AudioSegment.from_file(path)
    seg = seg.speedup(playback_speed=SPEEDUP)
    seg.export(path, format="mp3")
    logger.info(f"  Audio saved: {path}")


# def build_video(segments: List[str]):
#     logger.info("Step 4: Building video")
#     vclips, aclips = [], []

#     for idx, seg in enumerate(segments):
#         logger.info(f"  • Segment {idx+1}/{len(segments)}")
#         audio_fp = os.path.join(AUDIO_DIR, f"seg{idx}.mp3")
#         generate_audio(seg, audio_fp)

#         aclip = AudioFileClip(audio_fp)
#         aclips.append(aclip)

#         vclip = TextClip(
#             seg, fontsize=FONT_SIZE, font=FONT,
#             color=TEXT_COLOR, size=VIDEO_SIZE,
#             method="caption", bg_color=BG_COLOR
#         ).set_duration(aclip.duration).set_fps(FPS)
#         vclips.append(vclip)

#     final_vid   = concatenate_videoclips(vclips, method="compose")
#     final_audio = concatenate_audioclips(aclips)
#     final       = final_vid.set_audio(final_audio)

#     logger.info(f"Writing video to {VIDEO_FILE}")
#     final.write_videofile(
#         VIDEO_FILE,
#         codec="libx264",
#         audio_codec="aac",
#         fps=FPS,
#         temp_audiofile=os.path.join(OUTPUT_DIR, "temp-audio.m4a"),
#         remove_temp=True
#     )
#     logger.info("✅ Video built!")
def build_video(segments: List[str]):
    logger.info("Step 4: Building video over custom background")
    clips = []

    for idx, seg in enumerate(segments):
        logger.info(f"  • Segment {idx+1}/{len(segments)}")
        # 1) generate segment audio
        audio_fp = os.path.join(AUDIO_DIR, f"seg{idx}.mp3")
        generate_audio(seg, audio_fp)
        aclip = AudioFileClip(audio_fp)

        # 2) load the full‐frame background
        bg = ImageClip(BACKGROUND_IMAGE) \
            .set_duration(aclip.duration) \
            .set_fps(FPS) \
            .resize(VIDEO_SIZE)

        # 3) create the text clip, sized to right half (half width minus padding)
        text_width  = VIDEO_SIZE[0] // 2 - 40  # leave 40px margin
        txt = TextClip(
            seg,
            fontsize=FONT_SIZE,
            font=FONT,
            color=TEXT_COLOR,
            method="caption",
            size=(text_width, None)    # width fixed, height auto
        ).set_duration(aclip.duration)

        # 4) position text in the center of the right panel
        x_pos = VIDEO_SIZE[0] // 2 + 20  # left edge of right half + margin
        y_pos = ((VIDEO_SIZE[1] - txt.h) // 2) - 100
        txt = txt.set_position((x_pos, y_pos))

        # 5) composite background + text, attach audio
        clip = CompositeVideoClip([bg, txt]) \
               .set_audio(aclip) \
               .set_fps(FPS)

        clips.append(clip)

    # 6) stitch all segments together
    final = concatenate_videoclips(clips, method="compose")
    logger.info(f"Writing video to {VIDEO_FILE}")
    final.write_videofile(
        VIDEO_FILE,
        codec="libx264",
        audio_codec="aac",
        fps=FPS,
        temp_audiofile=os.path.join(OUTPUT_DIR, "temp-audio.m4a"),
        remove_temp=True
    )
    logger.info("✅ Video built!")


# ----------- YouTube Upload ------------

def get_youtube_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
    return build("youtube", "v3", credentials=creds)

def upload_video(file_path: str, articles: List[Article]):
    logger.info("Step 5: Uploading to YouTube")
    youtube = get_youtube_service()
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    title = f"News Shorts {today}"
    # build a short description
    desc = "Sources:\n"
    for art in articles[:10]:
        desc += f"- {art['title']} ({art['source']})\n"
    body = {
        "snippet": {
            "title": title,
            "description": desc,
            "tags": ["news","shorts","AI"],
            "categoryId": "25"
        },
        "status": {"privacyStatus":"public"}
    }
    media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
    req = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        status, response = req.next_chunk()
        if status:
            logger.info(f"  Upload progress: {int(status.progress()*100)}%")
    logger.info(f"✅ Uploaded: https://youtu.be/{response['id']}")


# ----------- Main Pipeline ----------

def main():
    logger.info("🚀 Starting pipeline")
    arts_all = fetch_all(limit_per_feed=10)
    arts_1   = filter_stage1(arts_all, top_k=50)
    arts_2   = filter_stage2(arts_1, top_k=20)
    segments = craft_script(arts_2)
    build_video(segments)
    upload_video(VIDEO_FILE, arts_2)
    logger.info(f"🎬 Completed! Video at {VIDEO_FILE}")

def lambda_handler(event, context):
    main()

if __name__ == "__main__":
    main()
