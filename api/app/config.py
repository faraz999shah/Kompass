"""Application settings, read once from environment variables."""

from functools import lru_cache
from pathlib import Path

from pydantic import AliasChoices, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[2]
FIVE_MEGABYTES = 5 * 1024 * 1024


class Settings(BaseSettings):
    """Every config value the API reads. Override any field with an env var of the same name."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_path: Path = Path("kompass.db")
    question_bank_dir: Path = REPO_ROOT / "data" / "question_bank"
    lesson_templates_dir: Path = REPO_ROOT / "data" / "lesson_templates"
    findex_dir: Path = REPO_ROOT / "data" / "findex"
    # Browser origins allowed to call the API (Expo web in local development).
    cors_allowed_origins: list[str] = Field(
        default=["http://localhost:8081", "http://127.0.0.1:8081"],
        validation_alias=AliasChoices("cors_allowed_origins", "cors_allow_origins"),
    )
    # Local-only test pages under /dev; off unless explicitly enabled.
    dev_tools_enabled: bool = False
    # Without an LLM key, English templates work; other lesson languages return 503.
    llm_api_key: SecretStr | None = None
    llm_model: str | None = None
    llm_base_url: str = "https://api.openai.com/v1"
    llm_timeout_seconds: float = Field(default=20.0, gt=0)
    # Optional reasoning effort for reasoning models, e.g. "low"; unset sends none.
    llm_reasoning_effort: str | None = None

    # Voice. Recordings over this size get 413 (docs/API_CONTRACTS.md).
    voice_max_audio_bytes: int = Field(default=FIVE_MEGABYTES, gt=0)
    voice_provider_timeout_seconds: float = Field(default=20.0, gt=0)
    # Transcribe and speak calls each client may make per minute; speech quota is small.
    voice_requests_per_minute: int = Field(default=30, gt=0)
    # Local development without a Gemini key: /transcribe returns a sample question.
    voice_dev_fixtures: bool = False

    # Speech via Gemini (see docs/adr/0007-gemini-for-speech.md): one key serves
    # both speech-to-text and text-to-speech. Without it, voice returns 503.
    gemini_api_key: SecretStr | None = None
    gemini_interactions_url: str = (
        "https://generativelanguage.googleapis.com/v1beta/interactions"
    )
    # Tried in order. On a Swahili clip 3.5 Flash-Lite answered in about 2 s
    # (500 free a day); the dedicated transcribe model took about 9 s (25 a day).
    gemini_transcribe_models: list[str] = [
        "gemini-3.5-flash-lite",
        "gemini-3.5-transcribe",
        "gemini-3.1-flash-lite",
        "gemini-3.8-flash",
    ]
    # 10 free requests a day each. Swahili needs a full Flash TTS model, so
    # Flash-Lite TTS is the last resort (English and Spanish only).
    gemini_tts_models: list[str] = [
        "gemini-3.8-flash-tts",
        "gemini-3.1-flash-tts-preview",
        "gemini-2.5-flash-preview-tts",
        "gemini-3.8-flash-lite-tts",
    ]
    gemini_tts_voice: str = "Kore"
    # Generated speech is reused for repeated text, which saves the small TTS quota.
    speech_cache_max_bytes: int = 50_000_000


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide settings; tests override this with dependency_overrides."""
    return Settings()
