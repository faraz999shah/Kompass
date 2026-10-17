"""Maps a short spoken reply to a voice command: an answer letter, next, back, repeat or help.

Pure and deterministic: no I/O and no LLM, so every rule is unit-tested and a
learner always gets the same result for the same words.
"""

import re
import unicodedata

from app.schemas.shared import Language
from app.schemas.voice import IntentResponse, VoiceCommand
from app.services import intent_vocabulary as vocabulary

_APOSTROPHES = re.compile(r"['\u2019]")
_NOT_LETTER_OR_DIGIT = re.compile(r"[^a-z0-9]+")


def normalize(text: str) -> str:
    """Lowercase the text and strip accents and punctuation: "¡Atrás!" -> "atras".

    Apostrophes are dropped rather than split on, so "it's" becomes "its".
    """
    decomposed = unicodedata.normalize("NFKD", _APOSTROPHES.sub("", text.lower()))
    without_accents = "".join(
        char for char in decomposed if not unicodedata.combining(char)
    )
    return _NOT_LETTER_OR_DIGIT.sub(" ", without_accents).strip()


def recognize_intent(text: str, language: Language) -> IntentResponse:
    """Return the command the reply asks for, or `unknown` if it is not one."""
    normalized = normalize(text)
    for candidate in _languages_to_try(language):
        words = _meaningful_words(normalized, candidate)
        command = _command(words, candidate)
        if command is not None:
            return IntentResponse(intent=command, normalized_text=normalized)
        letter = _answer_letter(words, candidate)
        if letter is not None:
            return IntentResponse(
                intent=VoiceCommand.OPTION, option_id=letter, normalized_text=normalized
            )
    return IntentResponse(intent=VoiceCommand.UNKNOWN, normalized_text=normalized)


def _languages_to_try(language: Language) -> list[Language]:
    """The learner's language first, then English, which many learners mix in."""
    return [language] if language == Language.EN else [language, Language.EN]


def _meaningful_words(normalized: str, language: Language) -> list[str]:
    """The reply's words without filler such as "um" or "please"."""
    fillers = vocabulary.FILLER_WORDS[language]
    return [word for word in normalized.split() if word not in fillers]


def _command(words: list[str], language: Language) -> VoiceCommand | None:
    """The navigation command the whole reply matches, if any."""
    phrase = " ".join(words)
    for command, phrases in vocabulary.COMMAND_PHRASES[language].items():
        if phrase in phrases:
            return command
    return None


def _answer_letter(words: list[str], language: Language) -> str | None:
    """The answer letter in replies like "b", "option c" or "the first one"."""
    lead_words = vocabulary.OPTION_LEAD_WORDS[language]
    core = [word for word in words if word not in lead_words]
    if len(core) == 1 and core[0] in vocabulary.LETTER_WORDS:
        return vocabulary.LETTER_WORDS[core[0]]
    ordinals = vocabulary.ORDINAL_WORDS[language]
    core = [word for word in core if word not in vocabulary.ORDINAL_TAIL_WORDS]
    if len(core) == 1 and core[0] in ordinals:
        return ordinals[core[0]]
    return None
