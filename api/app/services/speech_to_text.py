"""Checks a recording and turns it into text for Ask Kiko and voice mode.

Recordings are held in memory for the length of one request and never written
to disk or logged.
"""

from dataclasses import dataclass
from typing import Protocol

from app.schemas.shared import Language
from app.schemas.voice import TranscriptionResponse
from app.services.errors import (
    AudioTooLargeError,
    InvalidRequestError,
    UnsupportedAudioTypeError,
)

# Formats from docs/API_CONTRACTS.md, under the names phones and browsers send.
# expo-audio records AAC in an MPEG-4 container, which iOS labels audio/mp4.
ACCEPTED_AUDIO_TYPES = frozenset(
    {
        "audio/m4a",
        "audio/x-m4a",
        "audio/mp4",
        "audio/wav",
        "audio/x-wav",
        "audio/wave",
        "audio/webm",
        "audio/ogg",
        "audio/mpeg",
        "audio/mp3",
        "audio/aac",
    }
)

# Returned in development when no speech key is set, flagged with is_fixture.
SAMPLE_QUESTIONS = {
    Language.EN: "How do I start an emergency fund?",
    Language.ES: "¿Cómo empiezo un fondo de emergencia?",
    Language.SW: "Ninaanzaje mfuko wa dharura?",
}


@dataclass(frozen=True)
class AudioClip:
    """A recording that passed validation."""

    content: bytes
    content_type: str


class SpeechToTextProvider(Protocol):
    """A speech-to-text service."""

    is_fixture: bool

    async def transcribe(self, clip: AudioClip, language: Language) -> str:
        """Return the words in the clip, or "" when nothing was said."""
        ...


class SampleTranscriber:
    """Development stand-in that ignores the audio and returns a sample question."""

    is_fixture = True

    async def transcribe(self, clip: AudioClip, language: Language) -> str:
        """Return the sample question in the learner's language."""
        return SAMPLE_QUESTIONS[language]


def base_media_type(content_type: str | None) -> str:
    """The media type without parameters, e.g. "audio/webm;codecs=opus" -> "audio/webm"."""
    return (content_type or "").partition(";")[0].strip().lower()


def validate_recording(
    content: bytes, content_type: str | None, max_bytes: int
) -> AudioClip:
    """Accept a non-empty recording of a known type that fits the size limit.

    Raises:
        UnsupportedAudioTypeError: If the type is not an accepted audio format.
        AudioTooLargeError: If the recording is bigger than `max_bytes`.
        InvalidRequestError: If the recording is empty.
    """
    media_type = base_media_type(content_type)
    if media_type not in ACCEPTED_AUDIO_TYPES:
        raise UnsupportedAudioTypeError(
            f"Recordings of type '{media_type or 'unknown'}' are not accepted",
            {"accepted": sorted(ACCEPTED_AUDIO_TYPES)},
        )
    if len(content) > max_bytes:
        raise AudioTooLargeError("The recording is too large", {"max_bytes": max_bytes})
    if not content:
        raise InvalidRequestError("The recording is empty")
    return AudioClip(content=content, content_type=media_type)


async def transcribe(
    clip: AudioClip, language: Language, provider: SpeechToTextProvider
) -> TranscriptionResponse:
    """Transcribe the clip, marking sample output so the app can say so."""
    text = await provider.transcribe(clip, language)
    return TranscriptionResponse(
        text=text.strip(), language=language, is_fixture=provider.is_fixture
    )
