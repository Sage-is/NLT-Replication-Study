from __future__ import annotations

import json
import ssl
import sys
from dataclasses import dataclass
from urllib import error, request

from nlt.core.types import ChatCompletionRequest, ChatCompletionResponse, Message, Tool, ToolCall, Usage

DEFAULT_API_URL = "https://sage.startr.cloud/api/chat/completions"
DEFAULT_MODEL = "llama-3.1-8b-instant"


@dataclass
class SageClient:
    auth_token: str | None = None
    api_url: str = DEFAULT_API_URL
    default_model: str = DEFAULT_MODEL
    timeout: int = 60
    verify_tls: bool = True
    debug: bool = False

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

        if self.debug:
            print(f"[DEBUG] Making API request to: {self.api_url}", file=sys.stderr)
            print(f"[DEBUG] Model: {model or self.default_model}", file=sys.stderr)
            print(f"[DEBUG] Timeout: {self.timeout}s", file=sys.stderr)
            print(f"[DEBUG] Request payload: {json.dumps(payload, indent=2)}", file=sys.stderr)

        data = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"

        req = request.Request(
            self.api_url,
            data=data,
            headers=headers,
            method="POST",
        )

        context = None if self.verify_tls else ssl._create_unverified_context()

        if self.debug:
            import time
            print(f"[DEBUG] Starting API request at {time.strftime('%H:%M:%S')}", file=sys.stderr)
            
        try:
            with request.urlopen(req, context=context, timeout=self.timeout) as response:
                if self.debug:
                    print(f"[DEBUG] Got response with status: {response.status}", file=sys.stderr)
                response_data = json.loads(response.read().decode("utf-8"))
                if self.debug:
                    print(f"[DEBUG] Response completed at {time.strftime('%H:%M:%S')}", file=sys.stderr)
                    print(f"[DEBUG] Response data: {json.dumps(response_data, indent=2)}", file=sys.stderr)
        except error.HTTPError as exc:  # pragma: no cover - network
            if self.debug:
                print(f"[DEBUG] HTTP Error {exc.code}: {exc.reason}", file=sys.stderr)
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"HTTP {exc.code}: {body}") from exc
        except error.URLError as exc:  # pragma: no cover - network
            if self.debug:
                print(f"[DEBUG] URL Error: {exc.reason}", file=sys.stderr)
            raise RuntimeError(f"Network error: {exc.reason}") from exc
        except Exception as exc:
            if self.debug:
                print(f"[DEBUG] Unexpected error: {type(exc).__name__}: {exc}", file=sys.stderr)
            raise

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