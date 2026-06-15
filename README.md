# 🛡️ SHIELD Audio Downloader

Simple web app untuk download audio dari TikTok & Instagram.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install FFmpeg** (diperlukan untuk convert ke MP3):
   ```bash
   # macOS
   brew install ffmpeg
   
   # Linux
   sudo apt-get install ffmpeg
   
   # Windows
   choco install ffmpeg
   ```

3. **Run app:**
   ```bash
   streamlit run app.py
   ```

4. Buka browser ke `http://localhost:8501`

## Usage

- Paste TikTok atau Instagram link
- Klik "Download Audio"
- Audio akan di-convert ke MP3 dan bisa didownload langsung

## Supported Platforms

- ✅ TikTok
- ✅ Instagram (Reels, Posts)
- ✅ YouTube (bonus)
