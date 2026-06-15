# 🛡️ SHIELD Audio Downloader

Download & split audio dari TikTok & Instagram seperti Adobe Premiere / CapCut.

## Setup

1. **Install FFmpeg** (required untuk audio processing):
   ```bash
   # macOS
   brew install ffmpeg
   
   # Linux
   sudo apt-get install ffmpeg
   
   # Windows
   choco install ffmpeg
   ```

2. **Setup dengan uv:**
   ```bash
   uv sync
   uv run streamlit run app.py
   ```
   
   Atau dengan pip:
   ```bash
   pip install -r requirements.txt
   streamlit run app.py
   ```

3. Buka browser ke `http://localhost:8501`

## Features

### 📥 Download Tab
- Paste TikTok atau Instagram link
- Download audio langsung sebagai MP3

### ✂️ Split & Export Tab
- Upload audio dan split menjadi multiple segments
- Set split points dengan slider (dalam detik)
- Auto-generate naming: `audio_1.mp3`, `audio_2.mp3`, dst
- Batch download semua segments

## Contoh Naming
```
original_video_1.mp3  (0:00 - 0:15)
original_video_2.mp3  (0:15 - 0:30)
original_video_3.mp3  (0:30 - end)
```

## Supported Platforms

- ✅ TikTok
- ✅ Instagram (Reels, Posts)
- ✅ YouTube (bonus)
