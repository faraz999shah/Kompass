"""Request and response models for the voice endpoints under /v1/voice.

Mirrored in app/src/voice/types.ts; the endpoints are described in
docs/API_CONTRACTS.md (Voice API).
"""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.shared import Language

MAX_REPLY_LENGTH = 300
MAX_SPOKEN_TEXT_LENGTH = 1000


class VoiceCommand(StrEnum):
    """A spoken reply the app acts on. `unknown` tells the app to read the card again."""

    OPTION = "option"
    NEXT = "next"
    BACK = "back"
    REPEAT = "repeat"
    HELP = "help"
    UNKNOWN = "unknown"


class IntentRequest(BaseModel):
    """Body of POST /v1/voice/intent: a short transcribed reply."""

    model_config = ConfigDict(extra="forbid")

    text: str = Field(
        max_length=MAX_REPLY_LENGTH, description="What the learner said, as text."
    )
    language: Language = Field(description="Language the learner answered in.")


class IntentResponse(BaseModel):
    """The command a reply maps to."""

    intent: VoiceCommand = Field(description="The recognized command.")
    option_id: str | None = Field(
        default=None,
        pattern="^[a-d]$",
        description="The answer letter, set only when intent is `option`.",
    )
    normalized_text: str = Field(
        description="The reply lowercased, without accents or punctuation."
    )


class TranscriptionResponse(BaseModel):
    """Returned by POST /v1/voice/transcribe."""

    text: str = Field(description="What was said; empty when nothing was heard.")
    language: Language = Field(description="The language hint that was used.")
    is_fixture: bool = Field(
        default=False,
        description="True when a development sample was returned instead of a transcript.",
    )


class SpeakQuery(BaseModel):
    """Query parameters of GET /v1/voice/speak."""

    model_config = ConfigDict(extra="forbid")

    text: str = Field(
        min_length=1,
        max_length=MAX_SPOKEN_TEXT_LENGTH,
        description="What to say, normally a lesson card's voice.speak_text.",
    )
    language: Language = Field(description="Language of the text.")
