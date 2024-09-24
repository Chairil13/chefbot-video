import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
import re
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from PIL import Image

# Load the image
icon = Image.open("icon.png")

# Set the page config
st.set_page_config(
    page_title="Chef Bot",
    page_icon=icon,
    layout="centered"
)

# Load environment variables (ensure you have GOOGLE_API_KEY in your .env file)
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Define a more comprehensive prompt for the model
prompt = """You are a YouTube video summarizer. Your task is to analyze the 
following transcript text and provide a concise summary within 250 words. 
Highlight the key points, main arguments, and any important conclusions 
presented in the video. Respons summary in Bahasa Indonesia.
Transcript: """

# List kata kunci kuliner
keywords = ['food', 'food recipe', 'food ingredients', 'cookies', 'makanan', 'drnk', 'kitchen', 'cooking']

# Function untuk memeriksa apakah transkrip relevan dengan kuliner
def is_culinary_related(transcript_text, keywords):
    transcript_lower = transcript_text.lower()
    for keyword in keywords:
        if keyword in transcript_lower:
            return True
    return False

# Function to extract transcript text
def extract_transcript_details(youtube_video_url):
    try:
        video_id_pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
        match = re.search(video_id_pattern, youtube_video_url)
        
        if match:
            video_id = match.group(1)
        else:
            st.error("Format URL YouTube tidak valid. Pastikan Anda memasukkan URL yang benar.")
            return None

        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        except TranscriptsDisabled:
            st.warning("Transkripsi untuk video ini dinonaktifkan oleh pemilik konten.")
            return None
        except NoTranscriptFound:
            try:
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['id'])
            except:
                st.warning("Tidak ada transkripsi yang tersedia untuk video ini. Video mungkin tidak memiliki audio atau transkripsi.")
                return None

        transcript = " ".join([item["text"] for item in transcript_list])
        return transcript
    except Exception as e:
        st.error("Terjadi kesalahan saat memproses video. Pastikan video memiliki audio dan transkripsi tersedia.")
        return None

# Function to generate summary using Gemini Pro (replace with actual model)
def generate_gemini_content(transcript_text, prompt):
    # Replace with the actual code to interact with Gemini Pro
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + transcript_text) 
    return response.text

# Streamlit UI
st.title("YouTube Culinary Video Summarizer - Chef Bot 🧑‍🍳")
youtube_link = st.text_input("Paste link youtube nya disini:")

if youtube_link:
    # Extract video ID and display thumbnail (error handling included)
    try:
        video_id = youtube_link.split("=")[1]
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)
    except IndexError:
        st.warning("Format tautan YouTube tidak valid. Pastikan itu adalah URL video yang valid.")

# Columns for buttons
col1, col2 = st.columns(2)

# Button to get the summary
with col1:
    if st.button("Rangkum"):
        if youtube_link:  # Check if a link was provided
            transcript_text = extract_transcript_details(youtube_link)
            if transcript_text:  # Check if transcript extraction was successful
                # Cek apakah video kuliner
                if is_culinary_related(transcript_text, keywords):
                    with st.spinner("Sedang Merangkum..."):
                        summary = generate_gemini_content(transcript_text, prompt)
                        st.subheader("Rangkuman:")
                        st.write(summary)
                else:
                    st.warning("Video ini tidak tampak terkait dengan kuliner atau makanan.")
        else:
            st.warning("Silakan masukkan link video YouTube terlebih dahulu.")

# Button to get the full transcript
with col2:
    if st.button("Tampilkan semua transkip"):
        if youtube_link:
            transcript_text = extract_transcript_details(youtube_link)
            if transcript_text:
                # Cek apakah video kuliner
                if is_culinary_related(transcript_text, keywords):
                    st.subheader("Transkip Lengkap:")
                    st.text_area("", value=transcript_text, height=300)
                else:
                    st.warning("Video ini tidak tampak terkait dengan kuliner atau makanan.")
        else:
            st.warning("Silakan masukkan link video YouTube terlebih dahulu.")
