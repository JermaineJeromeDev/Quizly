from quiz_app.utils import (
    download_youtube_audio,
    generate_quiz_with_gemini,
    transcribe_audio_file,
)


def generate_quiz_from_youtube(video_url: str) -> dict:
    """Orchestriert den gesamten Prozess vom Download bis zum fertigen KI-Quiz."""
    audio_path = download_youtube_audio(video_url)
    transcript = transcribe_audio_file(audio_path)
    quiz_data = generate_quiz_with_gemini(transcript)
    return quiz_data
