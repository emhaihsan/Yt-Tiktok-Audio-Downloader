import streamlit as st
import yt_dlp
import os
from pathlib import Path

st.set_page_config(page_title="SHIELD Audio Downloader", layout="centered")

st.title("🛡️ SHIELD Audio Downloader")
st.markdown("Extract audio from TikTok & Instagram")

# Create downloads folder
DOWNLOADS_DIR = Path("downloads")
DOWNLOADS_DIR.mkdir(exist_ok=True)

url = st.text_input("Masukkan TikTok/Instagram link:", placeholder="https://www.tiktok.com/...")

if st.button("Download Audio"):
    if not url.strip():
        st.error("Masukkan URL terlebih dahulu!")
    else:
        try:
            with st.spinner("Downloading..."):
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'outtmpl': str(DOWNLOADS_DIR / '%(title)s.%(ext)s'),
                    'quiet': False,
                    'no_warnings': False,
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    filename = f"{info['title']}.mp3"
                    filepath = DOWNLOADS_DIR / filename

                st.success(f"✅ Berhasil download: {info['title']}")

                with open(filepath, "rb") as audio_file:
                    st.download_button(
                        label=f"📥 Download {filename}",
                        data=audio_file,
                        file_name=filename,
                        mime="audio/mpeg"
                    )

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
