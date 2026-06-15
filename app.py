import streamlit as st
import yt_dlp
import subprocess
import os
from pathlib import Path
from datetime import datetime
import json

st.set_page_config(page_title="SHIELD Audio Downloader", layout="wide")

st.title("🛡️ SHIELD Audio Downloader")
st.markdown("Download & Split audio dari TikTok & Instagram")

DOWNLOADS_DIR = Path("downloads")
DOWNLOADS_DIR.mkdir(exist_ok=True)

TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(exist_ok=True)

def format_time(seconds):
    mins = int(seconds) // 60
    secs = int(seconds) % 60
    return f"{mins}:{secs:02d}"

def get_audio_duration(filepath):
    cmd = [
        'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
        '-of', 'json', str(filepath)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    data = json.loads(result.stdout)
    return float(data['format']['duration'])

def split_audio(audio_path, split_points, title):
    """Split audio at given points (in seconds) and export as separate MP3s"""
    duration = get_audio_duration(audio_path)

    split_points = sorted(split_points)
    segments = []

    start = 0
    for i, end in enumerate(split_points):
        if start < end <= duration:
            segments.append((start, end, i+1))
            start = end

    if start < duration:
        segments.append((start, duration, len(segments) + 1))

    output_files = []
    progress_bar = st.progress(0)

    for idx, (start, end, seg_num) in enumerate(segments):
        output_name = f"{title}_{seg_num}.mp3"
        output_path = DOWNLOADS_DIR / output_name

        cmd = [
            'ffmpeg', '-i', str(audio_path),
            '-ss', str(start), '-to', str(end),
            '-q:a', '5', '-n',
            str(output_path)
        ]

        subprocess.run(cmd, capture_output=True, check=True)
        output_files.append(output_path)
        progress_bar.progress((idx + 1) / len(segments))

    return output_files, segments

# Tabs
tab1, tab2 = st.tabs(["📥 Download", "✂️ Split & Export"])

with tab1:
    st.subheader("Download Full Audio")
    url = st.text_input("Masukkan TikTok/Instagram link:", placeholder="https://www.tiktok.com/...", key="main_url")

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
                        'outtmpl': str(TEMP_DIR / '%(title)s.%(ext)s'),
                    }

                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=True)
                        filename = f"{info['title']}.mp3"
                        filepath = TEMP_DIR / filename

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

with tab2:
    st.subheader("Split & Export Bulk Audio")

    col1, col2 = st.columns([2, 1])

    with col1:
        split_url = st.text_input("Masukkan link untuk di-split:", placeholder="https://www.tiktok.com/...", key="split_url")

    with col2:
        num_splits = st.number_input("Jumlah potongan:", min_value=2, max_value=10, value=2)

    if split_url.strip():
        try:
            with st.spinner("Extracting audio..."):
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'outtmpl': str(TEMP_DIR / 'split_%(title)s.%(ext)s'),
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(split_url, download=True)
                    title = info['title']
                    filepath = TEMP_DIR / f"split_{title}.mp3"

            if filepath.exists():
                duration = get_audio_duration(filepath)
                st.info(f"📊 Duration: {format_time(duration)}")

                st.subheader("Set Split Points (dalam detik)")

                split_times = []
                cols = st.columns(num_splits - 1)

                for i, col in enumerate(cols):
                    with col:
                        time = st.slider(
                            f"Split {i+1}",
                            min_value=0.0,
                            max_value=float(duration),
                            step=1.0,
                            key=f"split_{i}"
                        )
                        split_times.append(time)

                split_times = sorted(set(split_times))

                st.write("📍 Split points:", [f"{format_time(t)}" for t in split_times])

                if st.button("✂️ Split & Export"):
                    output_files, segments = split_audio(filepath, split_times, title)

                    st.success(f"✅ Berhasil split menjadi {len(segments)} bagian!")

                    st.subheader("📥 Download Audio Splits")

                    cols = st.columns(len(output_files))
                    for col, output_file in zip(cols, output_files):
                        with col:
                            with open(output_file, "rb") as f:
                                st.download_button(
                                    label=f"📥 {output_file.name}",
                                    data=f.read(),
                                    file_name=output_file.name,
                                    mime="audio/mpeg",
                                    key=f"download_{output_file.name}"
                                )

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
