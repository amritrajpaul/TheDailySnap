#!/bin/bash
set -e

ENV_FILE="$HOME/.news_env.sh"
{
  echo "#!/bin/bash"
  for var in OPENAI_API_KEY ELEVENLABS_API_KEY ELEVENLABS_VOICE_ID \
      YOUTUBE_CLIENT_ID YOUTUBE_CLIENT_SECRET YOUTUBE_PROJECT_ID \
      YOUTUBE_AUTH_URI YOUTUBE_TOKEN_URI YOUTUBE_AUTH_PROVIDER_X509_CERT_URL \
      YOUTUBE_REDIRECT_URIS YOUTUBE_TOKEN_JSON GOOGLE_APPLICATION_CREDENTIALS; do
    if [ -n "${!var}" ]; then
      echo "export $var=\"${!var}\""
    fi
  done
} > "$ENV_FILE"
chmod 600 "$ENV_FILE"

CRON_TIME=${CRON_TIME:-"0 2 * * *"}
CRON_FILE=/etc/cron.d/news_shorts
echo "CRON_TZ=UTC" > "$CRON_FILE"
echo "$CRON_TIME bash -c 'source $ENV_FILE && cd /workspaces/TheDailySnap && python news_shorts.py >> /workspaces/TheDailySnap/cron.log 2>&1'" >> "$CRON_FILE"
chmod 0644 "$CRON_FILE"
crontab "$CRON_FILE"
service cron start
