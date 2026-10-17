// Types for the /v1/voice endpoints; they mirror api/app/schemas/voice.py.
import type { Language } from "@/src/types/api";

/** What a short spoken reply asks for; `unknown` means read the card again. */
export type VoiceCommand =
  "option" | "next" | "back" | "repeat" | "help" | "unknown";

/** Returned by POST /v1/voice/intent. */
export interface IntentResponse {
  intent: VoiceCommand;
  /** The answer letter, a to d, when `intent` is "option". */
  option_id: string | null;
  normalized_text: string;
}

/** Returned by POST /v1/voice/transcribe. */
export interface TranscriptionResponse {
  text: string;
  language: Language;
  /** True when the server returned a development sample, not a real transcript. */
  is_fixture: boolean;
}
