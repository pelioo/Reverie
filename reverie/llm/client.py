from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from openai import OpenAI
from openai import OpenAIError


@dataclass(slots=True)
class LLMConfig:
    model: str
    api_key: str
    base_url: str = "https://api.openai.com/v1"
    timeout_seconds: float = 60.0


@dataclass(slots=True)
class LLMToolCall:
    id: str
    name: str
    arguments_json: str


@dataclass(slots=True)
class LLMTurnResponse:
    content: str
    tool_calls: list[LLMToolCall] = field(default_factory=list)


class LLMError(RuntimeError):
    pass


class OpenAICompatibleClient:
    """Minimal OpenAI-compatible Chat Completions client (openai lib)."""

    def __init__(self, config: LLMConfig) -> None:
        self.config = config
        self.client = OpenAI(
            api_key=config.api_key,
            base_url=config.base_url,
            timeout=config.timeout_seconds,
        )

    def complete(
        self,
        messages: list[dict[str, Any]],
        temperature: float = 0.7,
        tools: list[dict[str, Any]] | None = None,
        tool_choice: str | dict[str, Any] | None = None,
    ) -> LLMTurnResponse:
        payload: dict[str, Any] = {
            "model": self.config.model,
            "messages": messages,
            "temperature": temperature,
        }
        if tools:
            payload["tools"] = tools
        if tool_choice is not None:
            payload["tool_choice"] = tool_choice

        try:
            response = self.client.chat.completions.create(**payload)
        except OpenAIError as e:
            raise LLMError(str(e)) from e

        try:
            message = response.choices[0].message
            content = (message.content or "").strip()
            calls: list[LLMToolCall] = []
            for tc in message.tool_calls or []:
                fn = tc.function
                calls.append(
                    LLMToolCall(
                        id=tc.id,
                        name=fn.name,
                        arguments_json=fn.arguments or "{}",
                    )
                )
            return LLMTurnResponse(content=content, tool_calls=calls)
        except Exception as e:  # noqa: BLE001
            raise LLMError(f"Invalid model response: {response}") from e

    def chat(self, messages: list[dict[str, Any]], temperature: float = 0.7) -> str:
        return self.complete(messages=messages, temperature=temperature).content
