"""Words the voice-command matcher understands, per language.

Every entry is already normalized (lowercase, no accents or punctuation), so
the matcher can compare it straight against a normalized reply. English is
also tried for Spanish and Swahili speakers, who often say "next" or "repeat".
"""

from app.schemas.shared import Language
from app.schemas.voice import VoiceCommand

COMMAND_PHRASES: dict[Language, dict[VoiceCommand, frozenset[str]]] = {
    Language.EN: {
        VoiceCommand.NEXT: frozenset(
            {"next", "continue", "go on", "next card", "next one", "keep going"}
        ),
        VoiceCommand.BACK: frozenset({"back", "go back", "previous", "last card"}),
        VoiceCommand.REPEAT: frozenset(
            {"repeat", "again", "say that again", "say it again", "what", "pardon"}
        ),
        VoiceCommand.HELP: frozenset(
            {"help", "help me", "what can i say", "i need help", "how does this work"}
        ),
    },
    Language.ES: {
        VoiceCommand.NEXT: frozenset(
            {"siguiente", "sigue", "seguir", "continuar", "continua", "adelante"}
        ),
        VoiceCommand.BACK: frozenset({"atras", "volver", "regresar", "anterior"}),
        VoiceCommand.REPEAT: frozenset(
            {"repite", "repetir", "otra vez", "de nuevo", "como", "que"}
        ),
        VoiceCommand.HELP: frozenset({"ayuda", "ayudame", "que puedo decir"}),
    },
    Language.SW: {
        VoiceCommand.NEXT: frozenset({"endelea", "ifuatayo", "mbele", "inayofuata"}),
        VoiceCommand.BACK: frozenset({"rudi", "rudi nyuma", "nyuma", "iliyopita"}),
        VoiceCommand.REPEAT: frozenset({"rudia", "sema tena", "tena", "nini"}),
        VoiceCommand.HELP: frozenset({"msaada", "nisaidie", "saidia"}),
    },
}

# Words that carry no meaning in a reply, dropped before matching.
FILLER_WORDS: dict[Language, frozenset[str]] = {
    Language.EN: frozenset(
        {"um", "uh", "er", "hmm", "ok", "okay", "so", "please", "kiko", "i", "think"}
    ),
    Language.ES: frozenset({"eh", "este", "pues", "bueno", "por", "favor", "kiko"}),
    Language.SW: frozenset({"eee", "basi", "sawa", "tafadhali", "kiko", "naomba"}),
}

# Words that can come before an answer letter: "option b", "la respuesta c".
OPTION_LEAD_WORDS: dict[Language, frozenset[str]] = {
    Language.EN: frozenset(
        {"option", "answer", "letter", "choice", "choose", "pick", "its", "the", "is"}
    ),
    Language.ES: frozenset(
        {"opcion", "respuesta", "letra", "la", "el", "es", "elijo", "escojo"}
    ),
    Language.SW: frozenset({"chaguo", "jibu", "herufi", "ni", "ya", "nachagua"}),
}

# How answer letters come back from speech-to-text, including spelled-out sounds.
LETTER_WORDS: dict[str, str] = {
    "a": "a",
    "ay": "a",
    "b": "b",
    "be": "b",
    "bee": "b",
    "c": "c",
    "ce": "c",
    "see": "c",
    "sea": "c",
    "d": "d",
    "de": "d",
    "dee": "d",
}

# Ordinals for learners who say "the first one" instead of a letter.
ORDINAL_WORDS: dict[Language, dict[str, str]] = {
    Language.EN: {"first": "a", "second": "b", "third": "c", "fourth": "d"},
    Language.ES: {
        "primera": "a",
        "primero": "a",
        "segunda": "b",
        "segundo": "b",
        "tercera": "c",
        "tercero": "c",
        "cuarta": "d",
        "cuarto": "d",
    },
    Language.SW: {"kwanza": "a", "pili": "b", "tatu": "c", "nne": "d"},
}

# Trailing words after an ordinal, as in "the first one" or "la primera opcion".
ORDINAL_TAIL_WORDS = frozenset({"one", "opcion", "respuesta", "chaguo", "jibu"})
