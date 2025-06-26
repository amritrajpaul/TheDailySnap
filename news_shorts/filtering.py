import json
from typing import List, Dict
import numpy as np
import openai
from . import config

Article = Dict[str, str]

if config.OPENAI_KEY:
    openai.api_key = config.OPENAI_KEY


def filter_stage1(articles: List[Article], top_k: int = 50) -> List[Article]:
    config.logger.info("Phase 1: Semantic filtering via embeddings")
    seed = "India politics commerce sports technology entertainment"
    texts = [seed] + [f"{a['title']} {a['summary']}" for a in articles]
    resp = config.with_retry(openai.embeddings.create, model="text-embedding-ada-002", input=texts)
    embs = resp.data
    seed_emb = np.array(embs[0].embedding)
    art_embs = np.array([e.embedding for e in embs[1:]])
    norms = np.linalg.norm(art_embs, axis=1) * np.linalg.norm(seed_emb)
    sims = (art_embs @ seed_emb) / norms
    idxs = np.argsort(-sims)[:top_k]
    filtered = [articles[i] for i in idxs]
    config.logger.info(f"  Kept top {len(filtered)} articles after embedding filter")
    config.logger.info("  Sample after Phase 1:")
    for a in filtered[:5]:
        config.logger.info(f"   • [{a['source']}] {a['title']}")
    return filtered


def filter_stage2(articles: List[Article], top_k: int = 20) -> List[Article]:
    config.logger.info("Phase 2: GPT rates newsworthiness")
    system = (
        "You are a news editor. Rate each of the following article headlines+summaries "
        "on a scale 1 (least) to 10 (most) for newsworthiness. "
        "Reply in JSON as a list of {\"index\": <i>, \"score\": <0-10>}"
    )
    user = "\n".join(
        f"{i}. {a['title']} — {a['summary']}" for i, a in enumerate(articles)
    )
    resp = config.with_retry(
        openai.chat.completions.create,
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0,
    )
    try:
        ratings = json.loads(resp.choices[0].message.content)
    except Exception:
        config.logger.warning("Could not parse ratings JSON, skipping Phase 2")
        return articles[:top_k]
    ratings.sort(key=lambda x: x["score"], reverse=True)
    top_idxs = [r["index"] for r in ratings[:top_k]]
    filtered = [articles[i] for i in top_idxs]
    config.logger.info(f"  Kept top {len(filtered)} after GPT rating")
    config.logger.info("  Sample after Phase 2:")
    for a in filtered[:5]:
        config.logger.info(f"   • [{a['source']}] {a['title']}")
    return filtered

