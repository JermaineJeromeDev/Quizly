import json
import os
import re

import whisper
import yt_dlp
from django.conf import settings
from google import genai
from google.genai import types
from google.genai.errors import ServerError


def download_youtube_audio(video_url: str):
    """Extract and download audio, returning both the local file path AND the clean YouTube ID."""
    output_path = os.path.join(settings.BASE_DIR, "media", "audio", "%(id)s.%(ext)s")
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "quiet": True,
        "noplaylist": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "extractor_args": {
            "youtube": ["player_client=android"]
        }
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=True)
        video_id = info['id']
        local_audio_path = os.path.join(settings.BASE_DIR, "media", "audio", f"{video_id}.mp3")
        
        return local_audio_path, video_id


def transcribe_audio_file(file_path: str) -> str:
    """Transcribe a local audio file into plain text using Whisper AI and clean up the file afterward."""
    model = whisper.load_model("tiny")
    result = model.transcribe(file_path)
    if os.path.exists(file_path):
        os.remove(file_path)
    return result["text"]


def build_gemini_prompt(transcript: str) -> str:
    """Construct the structured text prompt and target JSON schema constraints for the Gemini API model."""
    return f"""
    Basierend auf folgendem Transkript eines Videos, erstelle ein Quiz mit genau 10 Fragen.
    Jede Frage muss exakt 4 Antwortmoeglichkeiten besitzen. Eine davon ist die korrekte Antwort.
    
    Transkript:
    {transcript}
    
    Antworte AUSSCHLIESSLICH im folgenden JSON-Format (keine Markdowns wie ```json):
    {{
        "title": "Hier ein passender Quiz-Titel",
        "description": "Hier eine kurze Zusammenfassung",
        "questions": [
        {{
            "question_title": "Hier steht die Frage?",
            "question_options": ["Option A", "Option B", "Option C", "Option D"],
            "answer": "Option A"
        }}
        ]
    }}
    """


def execute_gemini_call(client, model_name: str, prompt: str) -> str:
    """Execute the concrete structural text content generation API request for a targeted Gemini model."""
    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json"),
    )
    return response.text


def generate_quiz_with_gemini(transcript: str) -> dict:
    """Orchestrate the JSON quiz dataset generation from text transcripts with automatic model degradation failovers."""
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    prompt = build_gemini_prompt(transcript)

    try:
        raw_text = execute_gemini_call(client, "gemini-2.5-flash", prompt)
    except ServerError:
        raw_text = execute_gemini_call(client, "gemini-1.5-flash", prompt)

    return json.loads(raw_text)


def generate_quiz_from_youtube(video_url: str) -> dict:
    """Orchestrates the single-pass download, transcription and clean URL construction for the frontend."""
    audio_path, video_id = download_youtube_audio(video_url)
    
    transcript = transcribe_audio_file(audio_path)
    quiz_data = generate_quiz_with_gemini(transcript)
    
    quiz_data["formatted_video_url"] = f"https://www.youtube.com/watch?v={video_id}"

    return quiz_data
