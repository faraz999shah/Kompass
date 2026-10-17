from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.config import Settings, get_settings
from app.dependencies import get_synthesizer, get_transcriber
from app.main import app
from app.schemas.shared import Language
from app.services.errors import SpeechUnavailableError
from app.services.speech_to_text import AudioClip

WAV = b"RIFF0000WAVE"
SMALL_LIMIT = 16


class StubTranscriber:
    is_fixture = False

    def __init__(self) -> None:
        self.languages: list[Language] = []

    async def transcribe(self, clip: AudioClip, language: Language) -> str:
        self.languages.append(language)
        return " How do I send money home? "


class StubSynthesizer:
    media_type = "audio/wav"

    async def synthesize(self, text: str, language: Language) -> bytes:
        return WAV


class BrokenSynthesizer:
    media_type = "audio/wav"

    async def synthesize(self, text: str, language: Language) -> bytes:
        raise SpeechUnavailableError("Gemini could not handle the voice request")


@pytest.fixture
def transcriber() -> StubTranscriber:
    return StubTranscriber()


@pytest.fixture
def client(transcriber: StubTranscriber) -> Iterator[TestClient]:
    app.dependency_overrides[get_settings] = lambda: Settings(
        voice_max_audio_bytes=SMALL_LIMIT, voice_requests_per_minute=1000
    )
    app.dependency_overrides[get_transcriber] = lambda: transcriber
    app.dependency_overrides[get_synthesizer] = StubSynthesizer
    yield TestClient(app)
    app.dependency_overrides.clear()


def upload(content: bytes, content_type: str = "audio/mp4") -> dict[str, object]:
    return {"files": {"audio": ("question.m4a", content, content_type)}}


def test_intent_returns_the_answer_letter(client: TestClient) -> None:
    response = client.post(
        "/v1/voice/intent", json={"text": "Opción B", "language": "es"}
    )

    assert response.status_code == 200
    assert response.json() == {
        "intent": "option",
        "option_id": "b",
        "normalized_text": "opcion b",
    }


def test_intent_rejects_unknown_languages(client: TestClient) -> None:
    response = client.post("/v1/voice/intent", json={"text": "next", "language": "fr"})

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "validation_error"


def test_transcribe_returns_trimmed_text_using_the_language_hint(
    client: TestClient, transcriber: StubTranscriber
) -> None:
    response = client.post(
        "/v1/voice/transcribe", data={"language": "sw"}, **upload(b"audio")
    )

    assert response.status_code == 200
    assert response.json() == {
        "text": "How do I send money home?",
        "language": "sw",
        "is_fixture": False,
    }
    assert transcriber.languages == [Language.SW]


@pytest.mark.parametrize(
    ("content", "content_type", "status", "code"),
    [
        (b"x" * (SMALL_LIMIT + 1), "audio/mp4", 413, "audio_too_large"),
        (b"audio", "image/png", 415, "unsupported_audio_type"),
        (b"", "audio/mp4", 400, "validation_error"),
    ],
)
def test_transcribe_rejects_bad_recordings(
    client: TestClient, content: bytes, content_type: str, status: int, code: str
) -> None:
    response = client.post(
        "/v1/voice/transcribe", data={"language": "en"}, **upload(content, content_type)
    )

    assert response.status_code == status
    assert response.json()["error"]["code"] == code


def test_transcribe_requires_a_language(client: TestClient) -> None:
    response = client.post("/v1/voice/transcribe", **upload(b"audio"))

    assert response.status_code == 400


def test_speak_streams_cacheable_wav(client: TestClient) -> None:
    response = client.get(
        "/v1/voice/speak", params={"text": "Habari", "language": "sw"}
    )

    assert response.status_code == 200
    assert response.content == WAV
    assert response.headers["content-type"] == "audio/wav"
    assert "max-age=86400" in response.headers["cache-control"]


@pytest.mark.parametrize("text", ["", "x" * 1001])
def test_speak_rejects_empty_or_overlong_text(client: TestClient, text: str) -> None:
    response = client.get("/v1/voice/speak", params={"text": text, "language": "en"})

    assert response.status_code == 400


def test_speak_failure_means_speech_is_unavailable(client: TestClient) -> None:
    app.dependency_overrides[get_synthesizer] = BrokenSynthesizer

    response = client.get("/v1/voice/speak", params={"text": "Hi", "language": "en"})

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "speech_unavailable"


def test_speech_is_unavailable_without_a_gemini_key() -> None:
    app.dependency_overrides[get_settings] = lambda: Settings(gemini_api_key="")
    try:
        response = TestClient(app).get(
            "/v1/voice/speak", params={"text": "Hi", "language": "en"}
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "speech_unavailable"


def test_speech_endpoints_are_rate_limited() -> None:
    app.dependency_overrides[get_settings] = lambda: Settings(
        voice_requests_per_minute=2
    )
    app.dependency_overrides[get_synthesizer] = StubSynthesizer
    try:
        client = TestClient(app, client=("10.0.0.9", 50000))
        statuses = [
            client.get(
                "/v1/voice/speak", params={"text": "Hi", "language": "en"}
            ).status_code
            for _ in range(3)
        ]
        limited = client.get("/v1/voice/speak", params={"text": "Hi", "language": "en"})
    finally:
        app.dependency_overrides.clear()

    assert statuses == [200, 200, 429]
    assert limited.json()["error"]["code"] == "rate_limited"
