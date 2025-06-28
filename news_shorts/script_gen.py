import json
from typing import List, Dict
import openai
import nltk
from nltk.tokenize import sent_tokenize
from . import config

Article = Dict[str, str]

if config.OPENAI_KEY:
    openai.api_key = config.OPENAI_KEY

# Ensure NLTK's Punkt tokenizer is available for sentence splitting
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")


def craft_script(articles: List[Article]) -> List[str]:
    """Craft a monologue and split into segments."""
    config.logger.info("Step 3: Crafting & segmenting John Oliver–style script")
    base_prompt = (
        "You are John Oliver, host of Last Week Tonight. Your mission is to inform citizens with clarity and wit,"
        " never sacrificing factual accuracy or journalistic integrity.\n"
        "Task:\n1) Write one seamless ~45-second monologue covering today's top five pillars: politics, commerce, sports, technology, entertainment."
    )
    if config.USE_ELEVENLABS:
        extra = (
            "2) Insert occasional emotion cues in square brackets like [giggle], [sigh] or [excited] so the script is expressive when read aloud by ElevenLabs.\n"
            "3) THEN split that monologue into 5–12 coherent segments for short-form video."
        )
    else:
        extra = (
            "2) THEN split that monologue into 5–12 coherent segments for short-form video."
        )
    system_prompt = (
        base_prompt
        + "\n"
        + extra
        + "\nRespond ONLY with a valid JSON object in this exact format:\n"
        + '{"segments": ["segment1", "segment2"]}'
        + "\nDo not include explanations, code fences, or any other text."
    )
    user_msg = "Here are today's pre-filtered articles:\n" + "\n".join(
        f"- [{a['source']}] {a['title']} — {a['summary']}" for a in articles
    )
    resp = config.with_retry(
        openai.chat.completions.create,
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_msg}],
        response_format={"type": "json_object"},
        temperature=0.7,
    )
    content = resp.choices[0].message.content
    try:
        data = json.loads(content)
        segs = data["segments"]
        assert isinstance(segs, list) and all(isinstance(s, str) for s in segs)
        config.logger.info(f"  ✓ GPT returned {len(segs)} segments")
        return segs
    except Exception as e:
        config.logger.warning(f"Segmentation JSON parse failed ({e}), falling back to sentences")
        return sent_tokenize(content)


def craft_hindi_script(articles: List[Article]) -> List[str]:
    """Craft a Hinglish monologue for Hindi shorts."""
    config.logger.info("Step 3H: Crafting Hinglish script")
    base_prompt = (
        "You are an energetic Hindi news anchor speaking in Hinglish (Hindi using Latin letters)."
        " Craft a single ~45 second monologue covering today's top stories."
    )
    if config.USE_ELEVENLABS:
        extra = (
            " Insert emotion cues in square brackets such as [hassna], [dukhi] or [excited] so ElevenLabs delivers with expression."
            " Then split the monologue into 5-12 short segments."
        )
    else:
        extra = " Then split the monologue into 5-12 short segments."
    system_prompt = (
        base_prompt
        + extra
        + " Respond ONLY with a JSON object like:\n"
        + '{"segments": ["seg1", "seg2"]}'
        + "\nDo not include explanations, code fences, or extra text."
    )
    user_msg = "Here are today's articles:\n" + "\n".join(
        f"- [{a['source']}] {a['title']} — {a['summary']}" for a in articles
    )
    resp = config.with_retry(
        openai.chat.completions.create,
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_msg}],
        response_format={"type": "json_object"},
        temperature=0.7,
    )
    content = resp.choices[0].message.content
    try:
        data = json.loads(content)
        segs = data["segments"]
        assert isinstance(segs, list) and all(isinstance(s, str) for s in segs)
        config.logger.info(f"  ✓ GPT returned {len(segs)} Hindi segments")
        return segs
    except Exception as e:
        config.logger.warning(f"Hindi segmentation JSON parse failed ({e}), falling back to sentences")
        return sent_tokenize(content)


def craft_daily_summary(articles: List[Article]) -> str:
    """Generate a concise, impartial summary."""
    config.logger.info("Step 3b: Crafting daily summary")
    system_prompt = (
        "You are a veteran news editor upholding journalistic integrity. Summarize today's most important international and Indian stories in under one minute."
    )
    user_msg = "\n".join(f"- {a['title']} ({a['source']})" for a in articles[:20])
    resp = config.with_retry(
        openai.chat.completions.create,
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_msg}],
        temperature=0,
    )
    summary = resp.choices[0].message.content.strip()
    config.logger.info("  ✓ Summary crafted")
    return summary

