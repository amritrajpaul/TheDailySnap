import os
import datetime
from typing import List, Dict
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from . import config

Article = Dict[str, str]


def get_youtube_service():
    creds = None
    if os.path.exists(config.TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(config.TOKEN_FILE, config.SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(config.CLIENT_SECRETS_FILE, config.SCOPES)
            creds = flow.run_local_server(port=0)
        with open(config.TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
    return build("youtube", "v3", credentials=creds)


def upload_video(file_path: str, articles: List[Article], title_prefix: str = "News Shorts") -> None:
    config.logger.info("Step 5: Uploading to YouTube")
    youtube = get_youtube_service()
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    title = f"{title_prefix} {today}"
    desc = "Sources:\n"
    for art in articles[:10]:
        desc += f"- {art['title']} ({art['source']})\n"
    body = {
        "snippet": {
            "title": title,
            "description": desc,
            "tags": ["news", "shorts", "AI"],
            "categoryId": "25",
        },
        "status": {"privacyStatus": "public"},
    }
    media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
    req = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        status, response = config.with_retry(req.next_chunk)
        if status:
            config.logger.info(f"  Upload progress: {int(status.progress() * 100)}%")
    config.logger.info(f"✅ Uploaded: https://youtu.be/{response['id']}")

