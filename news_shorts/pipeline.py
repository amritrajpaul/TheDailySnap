"""Main pipeline orchestrating the news short generation."""

from . import config
from .rss import fetch_all
from .filtering import filter_stage1, filter_stage2
from .script_gen import craft_script, craft_daily_summary
from .video_builder import build_video, build_summary_video
from .youtube_client import upload_video


def main() -> None:
    try:
        config.logger.info("🚀 Starting pipeline")
        arts_all = fetch_all()
        arts_1 = filter_stage1(arts_all, top_k=50)
        arts_2 = filter_stage2(arts_1, top_k=20)
        segments = craft_script(arts_2)
        build_video(segments)
        upload_video(config.VIDEO_FILE, arts_2)

        summary_text = craft_daily_summary(arts_2)
        build_summary_video(summary_text)
        upload_video(config.SUMMARY_FILE, arts_2, title_prefix="News Summary")
        config.logger.info(f"🎬 Completed! Video at {config.VIDEO_FILE}")
    except Exception as exc:
        config.logger.exception(f"Pipeline failed: {exc}")
        raise


def lambda_handler(event, context):
    main()


if __name__ == "__main__":
    main()

