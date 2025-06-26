import os
from typing import List
from moviepy.editor import (
    TextClip,
    AudioFileClip,
    concatenate_videoclips,
    CompositeVideoClip,
    ImageClip,
)
from . import config
from .tts_engine import generate_audio


def build_video(segments: List[str]) -> None:
    config.logger.info("Step 4: Building video over custom background")
    clips = []
    for idx, seg in enumerate(segments):
        config.logger.info(f"  • Segment {idx + 1}/{len(segments)}")
        audio_fp = os.path.join(config.AUDIO_DIR, f"seg{idx}.mp3")
        generate_audio(seg, audio_fp)
        aclip = AudioFileClip(audio_fp)
        bg = ImageClip(config.BACKGROUND_IMAGE).set_duration(aclip.duration).set_fps(config.FPS).resize(config.VIDEO_SIZE)
        text_width = config.VIDEO_SIZE[0] // 2 - 40
        txt = TextClip(
            seg,
            fontsize=config.FONT_SIZE,
            font=config.FONT,
            color=config.TEXT_COLOR,
            method="caption",
            size=(text_width, None),
        ).set_duration(aclip.duration)
        y_pos = ((config.VIDEO_SIZE[1] - txt.h) // 2) - 100
        txt = txt.set_position((config.VIDEO_SIZE[0] // 2 + 20, y_pos))
        clip = CompositeVideoClip([bg, txt]).set_audio(aclip).set_fps(config.FPS)
        clips.append(clip)
    final = concatenate_videoclips(clips, method="compose")
    config.logger.info(f"Writing video to {config.VIDEO_FILE}")
    config.with_retry(
        final.write_videofile,
        config.VIDEO_FILE,
        codec="libx264",
        audio_codec="aac",
        fps=config.FPS,
        temp_audiofile=os.path.join(config.OUTPUT_DIR, "temp-audio.m4a"),
        remove_temp=True,
    )
    config.logger.info("✅ Video built!")


def build_summary_video(text: str) -> None:
    config.logger.info("Step 4b: Building summary video")
    audio_fp = os.path.join(config.AUDIO_DIR, "summary.mp3")
    generate_audio(text, audio_fp)
    aclip = AudioFileClip(audio_fp)
    bg = ImageClip(config.BACKGROUND_IMAGE).set_duration(aclip.duration).set_fps(config.FPS).resize(config.VIDEO_SIZE)
    txt = (
        TextClip(
            text,
            fontsize=config.FONT_SIZE,
            font=config.FONT,
            color=config.TEXT_COLOR,
            method="caption",
            size=(config.VIDEO_SIZE[0] - 80, None),
        )
        .set_duration(aclip.duration)
        .set_position("center")
    )
    final = CompositeVideoClip([bg, txt]).set_audio(aclip)
    config.logger.info(f"Writing summary video to {config.SUMMARY_FILE}")
    config.with_retry(
        final.write_videofile,
        config.SUMMARY_FILE,
        codec="libx264",
        audio_codec="aac",
        fps=config.FPS,
        temp_audiofile=os.path.join(config.OUTPUT_DIR, "temp-audio.m4a"),
        remove_temp=True,
    )
    config.logger.info("✅ Summary video built!")

