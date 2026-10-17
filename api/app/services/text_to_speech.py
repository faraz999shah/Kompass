"""Server-side read-aloud for languages the phone cannot speak, usually Swahili.

The app speaks on the device whenever it can and calls GET /v1/voice/speak only
as a fallback, so any error here just means "use the device voice".
"""

from typing import Protocol

from app.schemas.shared import Language


class TextToSpeechProvider(Protocol):
    """A text-to-speech service."""

    media_type: str

    async def synthesize(self, text: str, language: Language) -> bytes:
        """Return audio of the text read aloud."""
        ...
