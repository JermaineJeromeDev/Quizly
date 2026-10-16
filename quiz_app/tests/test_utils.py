from unittest.mock import MagicMock, patch

from django.conf import settings

from quiz_app.utils import download_youtube_audio


@patch("quiz_app.utils.yt_dlp.YoutubeDL")
def test_download_youtube_audio_uses_default_player_clients(mock_youtube_dl) -> None:
    downloader = MagicMock()
    mock_youtube_dl.return_value.__enter__.return_value = downloader
    downloader.extract_info.return_value = {"id": "video-id"}

    audio_path, video_id = download_youtube_audio("https://www.youtube.com/watch?v=video-id")

    options = mock_youtube_dl.call_args.args[0]
    assert "extractor_args" not in options
    assert audio_path == str(settings.BASE_DIR / "media" / "audio" / "video-id.mp3")
    assert video_id == "video-id"
