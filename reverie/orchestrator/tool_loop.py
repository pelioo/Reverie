from __future__ import annotations

import json

from ..llm import OpenAICompatibleClient
from ..session_state import SessionStateManager
from ..tools import ToolRuntime
from .helpers import clean_reply, to_tool_call


class ToolLoopRunner:
    def __init__(
        self,
        *,
        llm_client: OpenAICompatibleClient,
        tool_runtime: ToolRuntime,
        session_state: SessionStateManager,
        temperature: float = 0.7,
        max_tool_steps: int = 3,
    ) -> None:
        self.llm_client = llm_client
        self.tool_runtime = tool_runtime
        self.session_state = session_state
        self.temperature = temperature
        self.max_tool_steps = max_tool_steps

    def run(self, messages: list[dict[str, object]]) -> tuple[str, str]:
        tools = self.tool_runtime.openai_tools()
        working_messages = list(messages)
        tool_notes: list[str] = []

        for _ in range(self.max_tool_steps):
            turn = self.llm_client.complete(
                messages=working_messages,
                temperature=self.temperature,
                tools=tools,
                tool_choice="auto",
            )

            if not turn.tool_calls:
                return clean_reply(turn.content), "\n\n".join(tool_notes)

            assistant_tool_calls: list[dict[str, object]] = []
            tool_messages: list[dict[str, object]] = []

            for call in turn.tool_calls:
                result, digest = self.tool_runtime.call_tool(to_tool_call(call))
                self.session_state.add_tool_result(digest.summary)

                if result.ok and result.tool_name == "sleep_request":
                    approved = float(result.raw.get("approved_seconds", 0.0))
                    if approved > 0:
                        self.session_state.set_sleep(approved)

                tool_notes.append(
                    self.tool_runtime.format_execution_log(
                        requested_tool=call.name,
                        result=result,
                        digest=digest,
                    )
                )
                assistant_tool_calls.append(
                    {
                        "id": call.id,
                        "type": "function",
                        "function": {"name": call.name, "arguments": call.arguments_json},
                    }
                )
                tool_messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": call.id,
                        "content": json.dumps(
                            {
                                "summary": digest.summary,
                                "key_facts": digest.key_facts,
                                "raw_ref": digest.raw_ref,
                                "ok": result.ok,
                                "error": result.error,
                            },
                            ensure_ascii=False,
                        ),
                    }
                )

            working_messages = working_messages + [
                {
                    "role": "assistant",
                    "content": turn.content or "",
                    "tool_calls": assistant_tool_calls,
                },
                *tool_messages,
            ]

        final = self.llm_client.complete(
            messages=working_messages,
            temperature=self.temperature,
            tools=tools,
            tool_choice="none",
        )
        return clean_reply(final.content), "\n\n".join(tool_notes)
