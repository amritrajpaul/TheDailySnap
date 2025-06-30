# News Shorts Application

An intelligent news aggregation and video generation system that creates engaging news shorts in both English and Hindi using AI-powered content analysis and text-to-speech technology.

## 🚀 Features

- **Smart News Aggregation**: Collects news from Indian and international outlets
- **AI-Powered Content Analysis**: Uses GPT-4 and embeddings for intelligent news filtering
- **International Coverage**: Includes top global sources alongside Indian outlets
- **Journalistic Integrity**: Prompts enforce factual accuracy and ethical standards
- **Multi-Language Support**: Generates content in English with optional Hindi voice-over
- **Expressive English Voice**: Supports ElevenLabs for more emotive delivery when credentials are provided
- **Automated Video Creation**: Creates vertical videos (720×1280) optimized for social media
- **YouTube Integration**: Automatic upload to YouTube with proper metadata
- **Content Management**: Intelligent ranking and categorization of news articles
- **Parallel Processing**: Optimized for speed with concurrent video processing
- **Hindi Video**: Generates a second video in Hinglish with Hindi voice-over

## 📋 Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Google Cloud credentials (for Hindi TTS)
- ElevenLabs API key (optional, for expressive English voice)
- YouTube API credentials
- FFmpeg (for video processing)
- ImageMagick (modify /etc/ImageMagick-6/policy.xml to allow read|write for pattern "@*")

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/newsShortsApp.git
   cd newsShortsApp
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install FFmpeg**
   - **Windows**: Download from [FFmpeg website](https://ffmpeg.org/download.html)
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt-get install ffmpeg`
4. **Install ImageMagick and update policy**
   - Install ImageMagick (e.g., `sudo apt-get install imagemagick`)
   - Edit `/etc/ImageMagick-6/policy.xml` and comment out `<policy domain="path" rights="none" pattern="@*"/>` or change `rights` to `read|write`


5. **Set up API credentials**
   - Create a `.env` file in the project root or define variables in your CI env.
   - At minimum set your API keys:
     ```
    OPENAI_API_KEY=your_openai_api_key
    GOOGLE_API_KEY=your_google_api_key
    ELEVENLABS_API_KEY=your_elevenlabs_api_key  # optional
    ELEVENLABS_VOICE_ID=your_voice_id           # optional
     ```
   - See `.env.example` for the list of all configurable variables

6. **Configure Google Cloud TTS**
   - Set up Google Cloud credentials
   - Update the path in the script:
     ```python
     os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path/to/your/credentials.json"
     ```

7. **Set up YouTube API**
   - Download `client_secrets.json` from Google Cloud Console
   - Place it in the project root

## 📁 Project Structure

```
TheDailySnap/
├── news_shorts/               # Package with pipeline
│   ├── __init__.py
│   ├── __main__.py            # Run with `python -m news_shorts`
│   ├── config.py              # Configuration and constants
│   ├── rss.py                 # RSS fetching utilities
│   ├── filtering.py           # Filtering logic
│   ├── script_gen.py          # GPT based script generation
│   ├── tts_engine.py          # Text-to-speech helpers
│   ├── video_builder.py       # Video creation helpers
│   ├── youtube_client.py      # Upload helper functions
│   └── pipeline.py            # Orchestration logic
├── assets/
│   └── background_fullframe.png
├── requirements.txt           # Python dependencies
├── .env.example               # Environment variables template
├── client_secrets.json        # YouTube API credentials (not committed)
├── .gitignore
└── README.md
```

## 🔧 Configuration

### RSS Sources
The application aggregates news from Indian and international media outlets including:
- The Hindu
- Indian Express
- Times of India
- Hindustan Times
- NDTV
- Economic Times
- BBC World
- CNN
- Al Jazeera
- And more...

### Content Categories
News is automatically categorized into:
- Politics
- Business
- Sports
- Technology
- Entertainment

### Video Settings
- Resolution: 720×1280 (vertical format)
- FPS: 24
- Codec: H.264
- Audio: AAC

### Environment Variables
Most behaviour can be configured with env vars or a `.env` file. Important options include:
- `GEN_AI_PROVIDER` chooses `openai` or `google` for script generation.
- `TTS_PROVIDER` selects `openai`, `elevenlabs` or `google` for speech.
- `VIDEO_LANGUAGES` sets which videos to make (e.g. `en,hi`).
- `UPLOAD_TO_YOUTUBE` set `0` to skip uploading.
- `OUTPUT_DIR` and `FILE_PREFIX` control where files are written.
See `.env.example` for the full list. You can also pass these variables via the `env` section of `.github/workflows/daily.yml`.
| Variable | Description | Default |
| --- | --- | --- |
| `OPENAI_API_KEY` | OpenAI API key | - |
| `GOOGLE_API_KEY` | Google Generative AI key | - |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to Google credentials JSON | - |
| `ELEVENLABS_API_KEY` | ElevenLabs TTS key | - |
| `ELEVENLABS_VOICE_ID` | ElevenLabs voice ID | - |
| `GEN_AI_PROVIDER` | `openai` or `google` | `openai` |
| `TTS_PROVIDER` | `openai`, `elevenlabs` or `google` | `openai` |
| `TTS_MODEL` | OpenAI speech model | `tts-1-hd` |
| `TTS_VOICE` | Voice name for OpenAI or ElevenLabs | `ash` |
| `GOOGLE_TTS_LANGUAGE` | Google TTS language code | `en-US` |
| `SPEEDUP` | Audio playback speed | `1.1` |
| `VIDEO_LANGUAGES` | Languages to produce (`en`, `hi`) | `en,hi` |
| `UPLOAD_TO_YOUTUBE` | Set `0` to skip uploading | `1` |
| `FEED_LIMIT` | RSS items per source | `15` |
| `OUTPUT_DIR` | Output folder | `output_v8_global` |
| `FILE_PREFIX` | Prefix for generated files | `news_short_v8_global` |
| `VIDEO_WIDTH` | Video width in pixels | `720` |
| `VIDEO_HEIGHT` | Video height in pixels | `1280` |
| `FONT` | Font family | `Arial` |
| `FONT_SIZE` | Font size | `36` |
| `TEXT_COLOR` | Overlay text color | `white` |
| `BG_COLOR` | Background color | `blue` |
| `FPS` | Frames per second | `24` |
| `RETRY_LIMIT` | API retry attempts | `3` |
| `YOUTUBE_CLIENT_ID` | OAuth client ID | - |
| `YOUTUBE_CLIENT_SECRET` | OAuth client secret | - |
| `YOUTUBE_PROJECT_ID` | Google Cloud project ID | - |
| `YOUTUBE_AUTH_URI` | OAuth auth URI | - |
| `YOUTUBE_TOKEN_URI` | OAuth token URI | - |
| `YOUTUBE_AUTH_PROVIDER_X509_CERT_URL` | Cert URL | - |
| `YOUTUBE_REDIRECT_URIS` | Allowed redirect URIs (comma separated) | - |
| `YOUTUBE_TOKEN_JSON` | Path to stored token JSON | - |

### Basic Usage
```bash
python -m news_shorts
```

### What the script does:
1. **News Aggregation**: Fetches latest news from RSS feeds
2. **Content Analysis**: Uses AI to filter and rank articles
3. **Script Generation**: Creates engaging scripts in English (optional Hindi voice-over)
4. **Audio Generation**: Uses OpenAI or Google TTS by default, switching to ElevenLabs when configured
5. **Video Creation**: Generates vertical videos with text overlays in English and Hindi
6. **YouTube Upload**: Automatically uploads videos to YouTube

### Output
- Main video: `$OUTPUT_DIR/${FILE_PREFIX}.mp4`
- Hindi video: `$OUTPUT_DIR/${FILE_PREFIX}_hi.mp4`

## ⚙️ Customization

### Modifying News Sources
Edit the `RSS_SOURCES` dictionary in the script:
```python
RSS_SOURCES = {
    "Your Source": "https://your-source.com/rss",
    # Add more sources here
}
```

### Adjusting Content Categories
Modify the categories in the `ContentManager` class:
```python
self.categories = {
    'your_category': ['keyword1', 'keyword2'],
    # Add more categories
}
```

### Changing Video Settings
Update the video configuration constants:
```python
VIDEO_SIZE = (720, 1280)  # Width, Height
FONT_SIZE = 36
TEXT_COLOR = "white"
FPS = 24
```

### Customizing Script Style
Modify the prompts in the `craft_script` function to change the tone and style of generated content.

## 🔒 Security

The `.gitignore` file ensures sensitive files are not committed:
- API keys and credentials
- Generated videos and audio files
- Cache files
- Environment variables

## 📊 Performance Optimization

- **Parallel Processing**: Uses ThreadPoolExecutor for concurrent video processing
- **Audio Caching**: Caches generated audio to avoid regeneration
- **Memory Management**: Proper cleanup of video clips and resources
- **Rate Limiting**: Exponential backoff for API calls

## 🐛 Troubleshooting

### Common Issues

1. **FFmpeg not found**
   - Ensure FFmpeg is installed and in your system PATH

2. **API rate limits**
   - The script includes retry logic with exponential backoff
   - Consider upgrading your API plan if hitting limits frequently

3. **Audio generation issues**
   - Check your OpenAI and Google Cloud API keys
   - Ensure proper internet connectivity

4. **Video generation errors**
   - Verify the background image exists
   - Check available disk space

### Debug Mode
Enable detailed logging by modifying the logging level:
```python
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for GPT-4 and TTS services
- Google Cloud for Hindi TTS
- MoviePy for video processing
- All RSS feed providers

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the configuration options

## 🔄 Updates

Stay updated with the latest features and improvements by:
- Starring the repository
- Watching for releases
- Following the project

---

**Note**: This application requires active API keys and internet connectivity to function properly. Ensure you have sufficient API credits before running the script. 
