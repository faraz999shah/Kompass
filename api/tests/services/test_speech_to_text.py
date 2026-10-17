import asyncio

import pytest

from app.schemas.shared import Language
from app.services.errors import (
    AudioTooLargeError,
    InvalidRequestError,
    UnsupportedAudioTypeError,
)
from app.services.speech_to_text import (
    SAMPLE_QUESTIONS,
    AudioClip,
    SampleTranscriber,
    transcribe,
    validate_recording,
)

LIMIT = 10


@pytest.mark.parametrize(
    "content_type",
    ["audio/mp4", "audio/m4a", "audio/webm;codecs=opus", "AUDIO/WAV", "audio/aac"],
)
def test_accepts_recordings_from_phones_and_browsers(content_type: str) -> None:
    clip = validate_recording(b"abc", content_type, LIMIT)

    assert clip.content == b"abc"
    assert ";" not in clip.content_type
    assert clip.content_type == clip.content_type.lower()


@pytest.mark.parametrize("content_type", [None, "", "video/mp4", "text/plain"])
def test_rejects_non_audio_uploads(content_type: str | None) -> None:
    with pytest.raises(UnsupportedAudioTypeError):
        validate_recording(b"abc", content_type, LIMIT)


def test_rejects_recordings_over_the_limit() -> None:
    with pytest.raises(AudioTooLargeError):
        validate_recording(b"x" * (LIMIT + 1), "audio/wav", LIMIT)


def test_accepts_a_recording_exactly_at_the_limit() -> None:
    assert validate_recording(b"x" * LIMIT, "audio/wav", LIMIT).content


def test_rejects_empty_recordings() -> None:
    with pytest.raises(InvalidRequestError):
        validate_recording(b"", "audio/wav", LIMIT)


@pytest.mark.parametrize("language", list(Language))
def test_sample_transcriber_answers_in_the_learner_language(language: Language) -> None:
    clip = AudioClip(content=b"abc", content_type="audio/wav")

    result = asyncio.run(transcribe(clip, language, SampleTranscriber()))

    assert result.text == SAMPLE_QUESTIONS[language]
    assert result.language == language
    assert result.is_fixture is True


class _PaddedTranscriber:
    is_fixture = False

    async def transcribe(self, clip: AudioClip, language: Language) -> str:
        return "  hello  "


def test_transcripts_are_trimmed_and_not_marked_as_samples() -> None:
    clip = AudioClip(content=b"abc", content_type="audio/wav")

    result = asyncio.run(transcribe(clip, Language.EN, _PaddedTranscriber()))

    assert result.text == "hello"
    assert result.is_fixture is False
