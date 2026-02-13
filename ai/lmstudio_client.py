"""LM Studio local AI client (OpenAI-compatible API)."""

import json
from typing import AsyncGenerator

import aiohttp

from ai.prompts import SYSTEM_PROMPT_STUB


class LMStudioClient:
    def __init__(self, base_url: str = "http://localhost:1234", model: str = "default"):
        self.base_url = base_url.rstrip("/")
        self.model = model

    async def test_connection(self) -> tuple:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/v1/models",
                    timeout=aiohttp.ClientTimeout(total=5),
                ) as resp:
                    if resp.status == 200:
                        return True, "Connected to LM Studio"
                    return False, f"Server returned status {resp.status}"
        except Exception as e:
            return False, f"Connection failed: {e}"

    async def generate(self, user_message: str,
                       context: dict = None) -> AsyncGenerator[str, None]:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT_STUB},
            {"role": "user", "content": user_message},
        ]
        payload = {"model": self.model, "messages": messages, "stream": True}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/v1/chat/completions",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=120),
                ) as resp:
                    if resp.status != 200:
                        yield f"Error: Server returned status {resp.status}"
                        return
                    async for line in resp.content:
                        line_str = line.decode("utf-8").strip()
                        if line_str.startswith("data: "):
                            data_str = line_str[6:]
                            if data_str == "[DONE]":
                                break
                            try:
                                data = json.loads(data_str)
                                chunk = (data.get("choices", [{}])[0]
                                         .get("delta", {}).get("content", ""))
                                if chunk:
                                    yield chunk
                            except (json.JSONDecodeError, IndexError):
                                continue
        except Exception as e:
            yield f"[Error: {e}]"
