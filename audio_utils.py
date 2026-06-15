import subprocess
import json
import librosa
import zipfile
from pathlib import Path

def format_time(seconds):
    """Convert seconds to MM:SS format"""
    mins = int(seconds) // 60
    secs = int(seconds) % 60
    return f"{mins}:{secs:02d}"

def get_audio_duration(filepath):
    """Get audio duration in seconds"""
    cmd = [
        'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
        '-of', 'json', str(filepath)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    data = json.loads(result.stdout)
    return float(data['format']['duration'])

def load_audio_waveform(filepath, sr=22050):
    """Load audio and extract waveform data"""
    y, sr = librosa.load(filepath, sr=sr)
    return y, sr

def split_audio(audio_path, cut_points, title, output_dir):
    """Split audio at given points and export as separate MP3s - yields progress"""
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

    for idx, (start, end, seg_num) in enumerate(segments):
        output_name = f"{title}_{seg_num}.mp3"
        output_path = output_dir / output_name

        cmd = [
            'ffmpeg', '-i', str(audio_path),
            '-ss', str(start), '-to', str(end),
            '-q:a', '5', '-n',
            str(output_path)
        ]

        subprocess.run(cmd, capture_output=True, check=True)
        yield idx + 1, len(segments)

def create_zip_download(files, output_dir):
    """Create ZIP file from multiple audio files"""
    zip_path = output_dir / "audio_splits.zip"

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file in files:
            zf.write(file, arcname=file.name)

    return zip_path
