import json
import os

import whisper
import yt_dlp
from django.conf import settings
from google import genai
from google.genai import types


def download_youtube_audio(video_url: str) -> str:
    """Laedt die Tonspur eines YouTube-Videos lokal als MP3 herunter."""
    output_path = os.path.join(settings.BASE_DIR, "media", "audio", "%(id)s.%(ext)s")
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=True)
        return os.path.join(settings.BASE_DIR, "media", "audio", f"{info['id']}.mp3")


def transcribe_audio_file(file_path: str) -> str:
    """Transkribiert eine lokale Audiodatei mit Whisper AI in Text."""
    model = whisper.load_model("base")
    result = model.transcribe(file_path)
    if os.path.exists(file_path):
        os.remove(file_path)
    return result["text"]


def build_gemini_prompt(transcript: str) -> str:
    """Baut den Prompt und die JSON-Strukturvorgabe fuer Gemini auf."""
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


def generate_quiz_with_gemini(transcript: str) -> dict:
    """Sendet das Transkript an Gemini Flash und gibt das strukturierte Quiz aus."""
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    prompt = build_gemini_prompt(transcript)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json"),
    )
    return json.loads(response.text)
