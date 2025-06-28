"""Main pipeline orchestrating the news short generation."""

from . import config
from .rss import fetch_all
from .filtering import filter_stage1, filter_stage2
from .script_gen import craft_script, craft_hindi_script
from .video_builder import build_video
from .youtube_client import upload_video


def main() -> None:
    try:
        config.logger.info("🚀 Starting pipeline")
        arts_all = fetch_all()
        arts_1 = filter_stage1(arts_all, top_k=50)
        arts_2 = filter_stage2(arts_1, top_k=20)
        segments = craft_script(arts_2)
        build_video(segments, video_path=config.VIDEO_FILE, audio_dir=config.AUDIO_DIR)
        upload_video(config.VIDEO_FILE, arts_2)

        h_segments = craft_hindi_script(arts_2)
        build_video(h_segments, video_path=config.HINDI_VIDEO_FILE, audio_dir=config.HINDI_AUDIO_DIR)
        upload_video(config.HINDI_VIDEO_FILE, arts_2, title_prefix="News Shorts Hindi")
        config.logger.info(f"🎬 Completed! Videos at {config.VIDEO_FILE} and {config.HINDI_VIDEO_FILE}")
    except Exception as exc:
        config.logger.exception(f"Pipeline failed: {exc}")
        raise


def lambda_handler(event, context):
    main()


if __name__ == "__main__":
    main()

