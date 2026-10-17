"""Domain errors raised by services. app/error_handlers.py maps each code to an HTTP status."""


class KompassError(Exception):
    """Base error carrying the contract's error code, message and details."""

    code = "internal_error"

    def __init__(self, message: str, details: dict[str, object] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class InvalidRequestError(KompassError):
    """The request is well-formed JSON but breaks a rule Pydantic cannot check."""

    code = "validation_error"


class ProfileNotFoundError(KompassError):
    """No profile exists, usually because onboarding never finished."""

    code = "profile_not_found"


class QuizNotFoundError(KompassError):
    """No quiz with this id belongs to this user."""

    code = "quiz_not_found"


class QuizAlreadySubmittedError(KompassError):
    """The quiz was already submitted or skipped."""

    code = "quiz_already_submitted"


class LessonNotFoundError(KompassError):
    """The lesson id is neither a core topic nor one of the learner's bonus lessons."""

    code = "lesson_not_found"


class LessonBuildError(KompassError):
    """A stored lesson could not be customized; a content or data bug, not the user's."""

    code = "lesson_build_failed"


class LessonGenerationError(KompassError):
    """The LLM could not produce a valid lesson for the request, even after a retry."""

    code = "lesson_generation_failed"


class OffTopicRequestError(KompassError):
    """The learner asked for a lesson that is not about personal money."""

    code = "off_topic_request"


class UnsupportedLanguageError(KompassError):
    """The language is valid but not offered for the chosen country."""

    code = "unsupported_language"


class UnsupportedAudioTypeError(KompassError):
    """The upload is not one of the recording formats the app sends."""

    code = "unsupported_audio_type"


class AudioTooLargeError(KompassError):
    """The upload is over the recording size limit."""

    code = "audio_too_large"


class SpeechUnavailableError(KompassError):
    """Speech is not configured, or the speech service failed; the app speaks on-device."""

    code = "speech_unavailable"


class RateLimitedError(KompassError):
    """The client sent too many voice requests in a short time."""

    code = "rate_limited"


class LessonTranslationError(KompassError):
    """A lesson could not be fully rewritten in the requested language."""

    code = "lesson_translation_failed"
