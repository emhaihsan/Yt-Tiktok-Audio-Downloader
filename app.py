import streamlit as st
import yt_dlp
import subprocess
import json
import librosa
import numpy as np
import plotly.graph_objects as go
import zipfile
from pathlib import Path

st.set_page_config(page_title="SHIELD Audio Downloader", layout="wide")

st.title("🛡️ SHIELD Audio Downloader")
st.markdown("Download & Cut audio dari TikTok & Instagram dengan Waveform Preview")

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

def load_audio_waveform(filepath, sr=22050):
    """Load audio dan extract waveform data"""
    y, sr = librosa.load(filepath, sr=sr)
    return y, sr

def create_waveform_plot(y, sr, duration, cut_points=[]):
    """Create interactive waveform plot dengan cut points"""
    times = np.linspace(0, duration, len(y))

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=times,
        y=y,
        mode='lines',
        name='Waveform',
        line=dict(color='#1f77b4', width=1),
        fill='tozeroy',
        fillcolor='rgba(31, 119, 180, 0.3)',
    ))

    for cut_point in sorted(cut_points):
        fig.add_vline(
            x=cut_point,
            line_dash="dash",
            line_color="red",
            annotation_text=f"CUT {format_time(cut_point)}",
            annotation_position="top"
        )

    fig.update_layout(
        title="Audio Waveform",
        xaxis_title="Time (seconds)",
        yaxis_title="Amplitude",
        hovermode='x unified',
        height=400,
        template="plotly_dark",
        xaxis=dict(
            rangeslider=dict(visible=False),
        )
    )

    return fig

def split_audio(audio_path, cut_points, title):
    """Split audio at given points dan export as separate MP3s"""
    duration = get_audio_duration(audio_path)
    cut_points = sorted(set(cut_points))

    segments = []
    start = 0

    for i, end in enumerate(cut_points):
        if start < end <= duration:
            segments.append((start, end, i + 1))
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

def create_zip_download(files):
    """Create ZIP file dari multiple audio files"""
    zip_path = DOWNLOADS_DIR / "audio_splits.zip"

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file in files:
            zf.write(file, arcname=file.name)

    return zip_path

# Tabs
tab1, tab2 = st.tabs(["📥 Download", "✂️ Cut & Export"])

with tab1:
    st.subheader("Download Full Audio")
    url = st.text_input("Masukkan TikTok/Instagram link:", placeholder="https://www.tiktok.com/...", key="main_url")

    if st.button("📥 Download Audio"):
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
    st.subheader("✂️ Cut & Export Bulk Audio")

    split_url = st.text_input("Masukkan link untuk di-cut:", placeholder="https://www.tiktok.com/...", key="split_url")

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

                st.info(f"📊 Duration: **{format_time(duration)}** | Total tracks: **{len(st.session_state.get('cut_points', []))}** CUT points")

                with st.spinner("Loading waveform..."):
                    y, sr = load_audio_waveform(filepath)

                if 'cut_points' not in st.session_state:
                    st.session_state.cut_points = []

                st.subheader("🎵 Waveform Preview")
                fig = create_waveform_plot(y, sr, duration, st.session_state.cut_points)
                st.plotly_chart(fig, use_container_width=True)

                st.subheader("➕ Add CUT Points")

                col1, col2 = st.columns([2, 1])

                with col1:
                    cut_time = st.slider(
                        "Click to select CUT point (seconds):",
                        min_value=0.0,
                        max_value=float(duration),
                        step=0.1,
                        key="cut_slider"
                    )

                with col2:
                    if st.button("🔪 Add CUT", use_container_width=True):
                        if cut_time not in st.session_state.cut_points and cut_time > 0 and cut_time < duration:
                            st.session_state.cut_points.append(cut_time)
                            st.session_state.cut_points.sort()
                            st.rerun()
                        else:
                            st.warning("CUT point already exists or invalid!")

                if st.session_state.cut_points:
                    st.subheader("🎯 Current CUT Points")

                    cols = st.columns(len(st.session_state.cut_points) + 1)

                    for idx, cut_point in enumerate(st.session_state.cut_points):
                        with cols[idx]:
                            col_a, col_b = st.columns([3, 1])
                            with col_a:
                                st.write(f"**{format_time(cut_point)}**")
                            with col_b:
                                if st.button("❌", key=f"remove_{idx}"):
                                    st.session_state.cut_points.pop(idx)
                                    st.rerun()

                    with cols[-1]:
                        if st.button("🗑️ Clear All", use_container_width=True):
                            st.session_state.cut_points = []
                            st.rerun()

                    if st.button("✂️ Generate Splits", use_container_width=True, type="primary"):
                        output_files, segments = split_audio(filepath, st.session_state.cut_points, title)

                        st.success(f"✅ Berhasil split menjadi {len(segments)} bagian!")

                        st.subheader("📥 Download Options")

                        col1, col2 = st.columns(2)

                        with col1:
                            st.write("**Individual Files:**")
                            for output_file in output_files:
                                with open(output_file, "rb") as f:
                                    st.download_button(
                                        label=f"📥 {output_file.name}",
                                        data=f.read(),
                                        file_name=output_file.name,
                                        mime="audio/mpeg",
                                        key=f"download_{output_file.name}",
                                        use_container_width=True
                                    )

                        with col2:
                            st.write("**Bulk Download:**")
                            zip_file = create_zip_download(output_files)
                            with open(zip_file, "rb") as f:
                                st.download_button(
                                    label="📦 Download as ZIP",
                                    data=f.read(),
                                    file_name=f"{title}_splits.zip",
                                    mime="application/zip",
                                    key="download_zip",
                                    use_container_width=True
                                )

                        st.session_state.cut_points = []

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
