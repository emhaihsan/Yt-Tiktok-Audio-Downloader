import streamlit as st
from pathlib import Path
from audio_utils import format_time, get_audio_duration, load_audio_waveform, split_audio, create_zip_download
from waveform import create_waveform_plot
from downloader import download_audio, download_audio_for_split

st.set_page_config(page_title="SHIELD Audio Downloader", layout="wide")

st.title("🛡️ SHIELD Audio Downloader")
st.markdown("Download & Cut audio dari TikTok & Instagram dengan Waveform Preview")

DOWNLOADS_DIR = Path("downloads")
DOWNLOADS_DIR.mkdir(exist_ok=True)

TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(exist_ok=True)

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
                    filepath, title = download_audio(url, TEMP_DIR)
                    st.success(f"✅ Berhasil download: {title}")

                    with open(filepath, "rb") as audio_file:
                        st.download_button(
                            label=f"📥 Download {filepath.name}",
                            data=audio_file,
                            file_name=filepath.name,
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
                filepath, title = download_audio_for_split(split_url, TEMP_DIR)

            if filepath.exists():
                duration = get_audio_duration(filepath)
                st.info(f"📊 Duration: **{format_time(duration)}** | Total CUT points: **{len(st.session_state.get('cut_points', []))}**")

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
                        progress_bar = st.progress(0)
                        status_text = st.empty()

                        output_files = []
                        for current, total in split_audio(filepath, st.session_state.cut_points, title, DOWNLOADS_DIR):
                            progress_bar.progress(current / total)
                            status_text.text(f"Processing: {current}/{total}")

                        st.success(f"✅ Berhasil split menjadi {total} bagian!")

                        st.subheader("📥 Download Options")

                        col1, col2 = st.columns(2)

                        with col1:
                            st.write("**Individual Files:**")
                            for output_file in sorted(DOWNLOADS_DIR.glob(f"{title}_*.mp3")):
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
                            output_files = list(DOWNLOADS_DIR.glob(f"{title}_*.mp3"))
                            zip_file = create_zip_download(output_files, DOWNLOADS_DIR)
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
