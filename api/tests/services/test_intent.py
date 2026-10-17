import pytest

from app.schemas.shared import Language
from app.schemas.voice import VoiceCommand
from app.services.intent import normalize, recognize_intent


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("¡Atrás!", "atras"),
        ("  Option   B. ", "option b"),
        ("Rudia, tafadhali", "rudia tafadhali"),
    ],
)
def test_normalize_lowercases_and_strips_accents_and_punctuation(
    text: str, expected: str
) -> None:
    assert normalize(text) == expected


@pytest.mark.parametrize(
    ("text", "language", "expected"),
    [
        ("Next", Language.EN, VoiceCommand.NEXT),
        ("go back", Language.EN, VoiceCommand.BACK),
        ("say that again", Language.EN, VoiceCommand.REPEAT),
        ("Help!", Language.EN, VoiceCommand.HELP),
        ("Siguiente", Language.ES, VoiceCommand.NEXT),
        ("Atrás", Language.ES, VoiceCommand.BACK),
        ("otra vez", Language.ES, VoiceCommand.REPEAT),
        ("ayúdame", Language.ES, VoiceCommand.HELP),
        ("Endelea", Language.SW, VoiceCommand.NEXT),
        ("rudi nyuma", Language.SW, VoiceCommand.BACK),
        ("rudia", Language.SW, VoiceCommand.REPEAT),
        ("msaada", Language.SW, VoiceCommand.HELP),
    ],
)
def test_recognizes_navigation_commands_in_every_language(
    text: str, language: Language, expected: VoiceCommand
) -> None:
    assert recognize_intent(text, language).intent == expected


@pytest.mark.parametrize(
    ("text", "language", "letter"),
    [
        ("b", Language.EN, "b"),
        ("Option C", Language.EN, "c"),
        ("I think it's bee", Language.EN, "b"),
        ("the first one", Language.EN, "a"),
        ("la respuesta d", Language.ES, "d"),
        ("la segunda opción", Language.ES, "b"),
        ("jibu a", Language.SW, "a"),
        ("ya tatu", Language.SW, "c"),
    ],
)
def test_recognizes_answer_letters_and_ordinals(
    text: str, language: Language, letter: str
) -> None:
    result = recognize_intent(text, language)

    assert result.intent == VoiceCommand.OPTION
    assert result.option_id == letter


def test_filler_words_are_ignored() -> None:
    assert recognize_intent("um, next please", Language.EN).intent == VoiceCommand.NEXT


def test_english_commands_work_for_spanish_and_swahili_speakers() -> None:
    assert recognize_intent("next", Language.SW).intent == VoiceCommand.NEXT
    assert recognize_intent("repeat", Language.ES).intent == VoiceCommand.REPEAT


@pytest.mark.parametrize(
    "text",
    ["", "I want to buy a house", "option e", "a or b", "next back"],
)
def test_anything_else_is_unknown(text: str) -> None:
    result = recognize_intent(text, Language.EN)

    assert result.intent == VoiceCommand.UNKNOWN
    assert result.option_id is None


def test_response_echoes_the_normalized_reply() -> None:
    assert recognize_intent("Siguiente!", Language.ES).normalized_text == "siguiente"
