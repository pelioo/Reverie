from __future__ import annotations

import json
import re

from ..llm import LLMToolCall
from ..tools import ToolCall


def to_tool_call(call: LLMToolCall) -> ToolCall:
    try:
        args = json.loads(call.arguments_json or "{}")
    except json.JSONDecodeError:
        args = {}
    return ToolCall(name=call.name, arguments=args)


def clean_reply(text: str) -> str:
    if not text:
        return ""
    cleaned = re.sub(r"<tool_call>.*?</tool_call>", "", text, flags=re.S)
    cleaned = re.sub(r"```json\s*\{.*?\}\s*```", "", cleaned, flags=re.S)
    cleaned = cleaned.replace("TOOL_CALL:", "")
    return cleaned.strip()


def compose_response(tag: str, reply: str, tool_notes: str) -> str:
    base = reply if tag == "user-turn" else f"[{tag}] {reply}"
    if tool_notes:
        return f"{base}\n[tool-result]\n{tool_notes}"
    return base
