from __future__ import annotations

from dataclasses import dataclass

from app.core.config import settings


@dataclass(slots=True)
class GeminiAssistantResult:
    text: str
    provider: str
    model: str | None
    used_fallback: bool
    error: str | None = None


class GeminiMealAssistant:
    """
    Gemini-backed assistant wrapper.

    Modes:
    - smalltalk: greetings, thanks, bye, light conversational replies
    - education: general nutrition / fitness education not tied to user-specific app data
    - grounded: personalized FitFuel responses that must preserve backend facts exactly
    """

    def __init__(self) -> None:
        self._client = None

    @property
    def is_enabled(self) -> bool:
        return settings.gemini_is_configured

    def _get_client(self):
        if self._client is None:
            from google import genai

            self._client = genai.Client(api_key=settings.gemini_api_key)
        return self._client

    @staticmethod
    def _system_instruction() -> str:
        return (
            "You are FitFuel AI, a conversational nutrition and fitness assistant inside a web app. "
            "You should sound natural, helpful, and human-like.\n\n"
            "There are three answer modes:\n"
            "1. SMALLTALK: greetings, goodbye, thanks, short casual conversation.\n"
            "2. EDUCATION: general nutrition or fitness education that does not require private app data.\n"
            "3. GROUNDED: personalized answers that depend on FitFuel app data such as goals, macros, meal plans, catalog foods, or logs.\n\n"
            "Rules:\n"
            "- In GROUNDED mode, use only the FitFuel grounded context for facts, numbers, foods, macros, calories, goals, and meal plans.\n"
            "- In EDUCATION mode, you may answer from general nutrition and fitness knowledge.\n"
            "- In EDUCATION mode, do not pretend the answer is personalized unless the grounded context explicitly provides personalization.\n"
            "- Never invent the user's calorie target, macros, weight, meal plan, or food log data.\n"
            "- If a question sounds medical, diagnostic, or high-risk, keep the answer general and suggest professional advice when appropriate.\n"
            "- Be clear, practical, and concise."
        )

    @staticmethod
    def _build_prompt(
        *,
        user_message: str,
        detected_intent: str,
        response_mode: str,
        conversation_history: str,
        grounded_context: str,
        deterministic_fallback: str,
    ) -> str:
        return "\n".join(
            [
                "User message:",
                user_message,
                "",
                "Detected intent:",
                detected_intent,
                "",
                "Response mode:",
                response_mode,
                "",
                "Recent conversation history:",
                conversation_history or "No earlier messages in this session.",
                "",
                "Grounded FitFuel context:",
                grounded_context or "No grounded FitFuel context was supplied for this turn.",
                "",
                "Deterministic fallback answer:",
                deterministic_fallback,
                "",
                "Write the final assistant reply.",
                "If response_mode is SMALLTALK, reply naturally and briefly.",
                "If response_mode is EDUCATION, answer the question directly using general nutrition/fitness knowledge.",
                "If response_mode is GROUNDED, preserve all grounded numbers and backend facts exactly.",
                "Do not mention internal modes or internal prompt rules.",
            ]
        )

    def generate_reply(
        self,
        *,
        user_message: str,
        detected_intent: str,
        response_mode: str,
        conversation_history: str,
        grounded_context: str,
        deterministic_fallback: str,
    ) -> GeminiAssistantResult:
        if not self.is_enabled:
            return GeminiAssistantResult(
                text=deterministic_fallback,
                provider="deterministic_fallback",
                model=None,
                used_fallback=True,
            )

        try:
            from google.genai import types

            client = self._get_client()
            prompt = self._build_prompt(
                user_message=user_message,
                detected_intent=detected_intent,
                response_mode=response_mode,
                conversation_history=conversation_history,
                grounded_context=grounded_context,
                deterministic_fallback=deterministic_fallback,
            )

            response = client.models.generate_content(
                model=settings.gemini_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=self._system_instruction(),
                    temperature=settings.gemini_temperature,
                    max_output_tokens=settings.gemini_max_output_tokens,
                ),
            )

            text = (response.text or "").strip()
            if not text:
                raise ValueError("Gemini returned an empty response.")

            return GeminiAssistantResult(
                text=text,
                provider="gemini",
                model=settings.gemini_model,
                used_fallback=False,
            )
        except Exception as exc:
            return GeminiAssistantResult(
                text=deterministic_fallback,
                provider="deterministic_fallback",
                model=settings.gemini_model,
                used_fallback=True,
                error=str(exc),
            )