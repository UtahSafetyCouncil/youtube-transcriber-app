import os
import platform
import zipfile
import urllib.request

def install_ffmpeg():
    ffmpeg_path = os.path.abspath("ffmpeg/bin/ffmpeg.exe")
    if platform.system() == "Windows" and not os.path.exists(ffmpeg_path):
        print("Downloading ffmpeg...")
        url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
        zip_path = "ffmpeg.zip"
        urllib.request.urlretrieve(url, zip_path)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall("ffmpeg")
        os.remove(zip_path)
        print("ffmpeg downloaded and extracted.")

    # Add Linux or Mac here if you want cross-platform support

    # Add ffmpeg bin to PATH so yt-dlp and whisper find it
    ffmpeg_bin_dir = os.path.abspath("ffmpeg/bin")
    os.environ["PATH"] += os.pathsep + ffmpeg_bin_dir

install_ffmpeg()

import streamlit as st
import subprocess
import os
import imageio_ffmpeg
import os

ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
os.environ["FFMPEG_PATH"] = ffmpeg_path

import torch
torch.classes.__path__ = []  # Fixes Streamlit import warning
import os
os.environ["FFMPEG_PATH"] = ffmpeg_path
import whisper
import yt_dlp
from datetime import datetime

# Title
st.title("🎬 YouTube Video Transcriber & Content Helper")

# Input field
youtube_url = st.text_input("Paste your YouTube video URL below:")

if youtube_url:
    st.info("Processing video... This may take a few minutes.")
    
    # Step 1: Download video audio using yt-dlp
    output_filename = "audio.mp3"
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_filename,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])
        st.success("✅ Audio downloaded!")

        # Step 2: Transcribe using Whisper
        model = whisper.load_model("base")
        result = model.transcribe(output_filename)
        transcript = result["text"]
        st.success("✅ Transcription complete!")

        # Show transcript
        st.subheader("📝 Transcript")
        st.text_area("Full transcript:", transcript, height=300)

        # Step 3: Suggest a title and hashtags
        st.subheader("📌 Suggested Title & Hashtags")

        if transcript:
            words = transcript.split()
            summary = " ".join(words[:12]) + "..." if len(words) > 12 else transcript
            st.write("**Title Idea:**", f"`{summary}`")

            keywords = [w.lower().strip("#.,") for w in words if len(w) > 5]
            top_tags = list(set(keywords))[:5]
            hashtags = " ".join([f"#{tag}" for tag in top_tags])
            st.write("**Hashtags:**", hashtags)
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
