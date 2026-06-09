"""Orchestration service layer for assembling processing components into a cohesive workflow."""

from quiz_app.utils import (
    download_youtube_audio,
    generate_quiz_with_gemini,
    transcribe_audio_file,
)


def generate_quiz_from_youtube(video_url: str) -> dict:
    """Orchestrate the entire pipeline from video audio extraction to final AI quiz generation."""
    audio_path = download_youtube_audio(video_url)
    transcript = transcribe_audio_file(audio_path)
    quiz_data = generate_quiz_with_gemini(transcript)
    return quiz_data
