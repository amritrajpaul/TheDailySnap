import os
import datetime
import json
import tempfile
from typing import List, Dict
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from . import config

Article = Dict[str, str]


def get_youtube_service():
    config.write_client_secrets()
    creds = None

    if config.YOUTUBE_TOKEN_JSON:
        creds = Credentials.from_authorized_user_info(json.loads(config.YOUTUBE_TOKEN_JSON), config.SCOPES)
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
    elif os.path.exists(config.TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(config.TOKEN_FILE, config.SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if config.YOUTUBE_CLIENT_ID and config.YOUTUBE_CLIENT_SECRET:
                data = {
                    "installed": {
                        "client_id": config.YOUTUBE_CLIENT_ID,
                        "client_secret": config.YOUTUBE_CLIENT_SECRET,
                        "project_id": config.YOUTUBE_PROJECT_ID or "",
                        "auth_uri": config.YOUTUBE_AUTH_URI or "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": config.YOUTUBE_TOKEN_URI or "https://oauth2.googleapis.com/token",
                        "auth_provider_x509_cert_url": config.YOUTUBE_AUTH_PROVIDER_X509_CERT_URL or "https://www.googleapis.com/oauth2/v1/certs",
                        "redirect_uris": config.YOUTUBE_REDIRECT_URIS.split(",") if config.YOUTUBE_REDIRECT_URIS else ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"],
                    }
                }
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
                json.dump(data, tmp)
                tmp.flush()
                flow = InstalledAppFlow.from_client_secrets_file(tmp.name, config.SCOPES)
            else:
                flow = InstalledAppFlow.from_client_secrets_file(config.CLIENT_SECRETS_FILE, config.SCOPES)
            creds = flow.run_local_server(port=0)
        if not config.YOUTUBE_TOKEN_JSON:
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

