"""Voice endpoints: transcribe a recording, map a reply to a command, read text aloud.

HTTP only. The rules live in services/speech_to_text.py and services/intent.py,
and the speech services are injected by app/dependencies.py.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, Query, Response, UploadFile, status

from app.dependencies import (
    SettingsDep,
    get_synthesizer,
    get_transcriber,
    limit_voice_requests,
)
from app.schemas.shared import ErrorResponse, Language
from app.schemas.voice import (
    IntentRequest,
    IntentResponse,
    SpeakQuery,
    TranscriptionResponse,
)
from app.services import intent, speech_to_text
from app.services.speech_to_text import SpeechToTextProvider
from app.services.text_to_speech import TextToSpeechProvider

router = APIRouter(prefix="/v1/voice", tags=["voice"])

TranscriberDep = Annotated[SpeechToTextProvider, Depends(get_transcriber)]
SynthesizerDep = Annotated[TextToSpeechProvider, Depends(get_synthesizer)]
SPEECH_CACHE_HEADER = "public, max-age=86400"

_INVALID = {status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse}}
_SPEECH_ERRORS = {
    **_INVALID,
    status.HTTP_429_TOO_MANY_REQUESTS: {"model": ErrorResponse},
    status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ErrorResponse},
}


@router.post(
    "/intent",
    response_model=IntentResponse,
    summary="Turn a short spoken reply into a command",
    responses=_INVALID,
)
def post_intent(request: IntentRequest) -> IntentResponse:
    """Return an answer letter, next, back, repeat, help, or unknown."""
    return intent.recognize_intent(request.text, request.language)


@router.post(
    "/transcribe",
    response_model=TranscriptionResponse,
    summary="Transcribe a spoken question or reply",
    dependencies=[Depends(limit_voice_requests)],
    responses={
        **_SPEECH_ERRORS,
        status.HTTP_413_CONTENT_TOO_LARGE: {"model": ErrorResponse},
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: {"model": ErrorResponse},
    },
)
async def post_transcribe(
    audio: Annotated[UploadFile, File(description="The recording, e.g. m4a or webm.")],
    language: Annotated[Language, Form(description="Language hint for the speaker.")],
    settings: SettingsDep,
    transcriber: TranscriberDep,
) -> TranscriptionResponse:
    """Transcribe the recording in memory; it is never stored."""
    # One byte over the limit is enough to reject a large upload without reading it all.
    content = await audio.read(settings.voice_max_audio_bytes + 1)
    clip = speech_to_text.validate_recording(
        content, audio.content_type, settings.voice_max_audio_bytes
    )
    return await speech_to_text.transcribe(clip, language, transcriber)


@router.get(
    "/speak",
    response_class=Response,
    summary="Read text aloud as audio",
    dependencies=[Depends(limit_voice_requests)],
    responses={
        status.HTTP_200_OK: {"content": {"audio/wav": {}}, "description": "WAV audio."},
        **_SPEECH_ERRORS,
    },
)
async def get_speak(
    query: Annotated[SpeakQuery, Query()], synthesizer: SynthesizerDep
) -> Response:
    """Return the text read aloud; a GET so audio players can stream the URL."""
    audio = await synthesizer.synthesize(query.text, query.language)
    return Response(
        content=audio,
        media_type=synthesizer.media_type,
        headers={"Cache-Control": SPEECH_CACHE_HEADER},
    )
