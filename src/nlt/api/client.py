from __future__ import annotations

import json
import ssl
from dataclasses import dataclass
from urllib import error, request

from nlt.core.types import ChatCompletionRequest, ChatCompletionResponse, Message, Tool, ToolCall, Usage

DEFAULT_API_URL = "https://sage.startr.cloud/api/chat/completions"
DEFAULT_MODEL = "llama-3.1-8b-instant"


@dataclass
class SageClient:
    auth_token: str
    api_url: str = DEFAULT_API_URL
    default_model: str = DEFAULT_MODEL
    timeout: int = 60
    verify_tls: bool = True

    def chat_completion(
        self,
        messages: list[Message],
        model: str | None = None,
        stream: bool = False,
        tools: list[Tool] | None = None,
        tool_choice: str | None = None,
    ) -> ChatCompletionResponse:
        payload = ChatCompletionRequest(
            model=model or self.default_model,
            messages=messages,
            stream=stream,
            tools=tools,
            tool_choice=tool_choice,
        ).to_wire()

        data = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.auth_token}",
        }

        req = request.Request(
            self.api_url,
            data=data,
            headers=headers,
            method="POST",
        )

        context = None if self.verify_tls else ssl._create_unverified_context()

        try:
            with request.urlopen(req, context=context, timeout=self.timeout) as response:
                response_data = json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:  # pragma: no cover - network
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"HTTP {exc.code}: {body}") from exc
        except error.URLError as exc:  # pragma: no cover - network
            raise RuntimeError(f"Network error: {exc.reason}") from exc

        content = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
        usage_dict: dict[str, int] = response_data.get("usage", {}) or {}
        usage = Usage(
            prompt_tokens=usage_dict.get("prompt_tokens"),
            completion_tokens=usage_dict.get("completion_tokens"),
            total_tokens=usage_dict.get("total_tokens"),
        )

        # Parse tool_calls if present
        tool_calls: list[ToolCall] = []
        raw_tool_calls = response_data.get("choices", [{}])[0].get("message", {}).get("tool_calls", [])
        if raw_tool_calls:
            for tc in raw_tool_calls:
                tool_calls.append(
                    ToolCall(
                        id=tc.get("id", ""),
                        type=tc.get("type", "function"),
                        function=tc.get("function", {}),
                    )
                )

        return ChatCompletionResponse(content=content, raw=response_data, usage=usage, tool_calls=tool_calls)

    def simple_chat(self, user_message: str, model: str | None = None) -> str:
        response = self.chat_completion(messages=[Message(role="user", content=user_message)], model=model)
        return response.content