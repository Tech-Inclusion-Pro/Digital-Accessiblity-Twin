"""Cloud AI client supporting OpenAI and Anthropic APIs."""

import json
from typing import AsyncGenerator

import aiohttp

from ai.prompts import SYSTEM_PROMPT_STUB


class CloudClient:
    def __init__(self, provider: str, model: str, api_key: str):
        self.provider = provider
        self.model = model
        self.api_key = api_key

    async def test_connection(self) -> tuple:
        if not self.api_key:
            return False, "API key is required for cloud providers"
        try:
            if self.provider == "openai":
                async with aiohttp.ClientSession() as session:
                    headers = {"Authorization": f"Bearer {self.api_key}"}
                    async with session.get(
                        "https://api.openai.com/v1/models",
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=10),
                    ) as resp:
                        if resp.status == 200:
                            return True, "Connected to OpenAI"
                        return False, f"API returned status {resp.status}"

            elif self.provider == "anthropic":
                if self.api_key.startswith("sk-ant-"):
                    return True, "Anthropic API key format valid"
                return False, "Invalid API key format"

            return False, f"Provider '{self.provider}' not supported"
        except Exception as e:
            return False, f"Connection failed: {e}"

    async def generate(self, user_message: str,
                       context: dict = None) -> AsyncGenerator[str, None]:
        if self.provider == "openai":
            async for chunk in self._generate_openai(user_message):
                yield chunk
        elif self.provider == "anthropic":
            async for chunk in self._generate_anthropic(user_message):
                yield chunk
        else:
            yield f"Provider '{self.provider}' not implemented."

    async def _generate_openai(self, user_message: str) -> AsyncGenerator[str, None]:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT_STUB},
            {"role": "user", "content": user_message},
        ]
        payload = {"model": self.model, "messages": messages, "stream": True}
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.openai.com/v1/chat/completions",
                    json=payload, headers=headers,
                    timeout=aiohttp.ClientTimeout(total=120),
                ) as resp:
                    if resp.status != 200:
                        data = await resp.json()
                        yield f"Error: {data.get('error', {}).get('message', 'Unknown')}"
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

    async def _generate_anthropic(self, user_message: str) -> AsyncGenerator[str, None]:
        messages = [{"role": "user", "content": user_message}]
        payload = {
            "model": self.model,
            "max_tokens": 4096,
            "system": SYSTEM_PROMPT_STUB,
            "messages": messages,
            "stream": True,
        }
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.anthropic.com/v1/messages",
                    json=payload, headers=headers,
                    timeout=aiohttp.ClientTimeout(total=120),
                ) as resp:
                    if resp.status != 200:
                        data = await resp.json()
                        yield f"Error: {data.get('error', {}).get('message', 'Unknown')}"
                        return
                    async for line in resp.content:
                        line_str = line.decode("utf-8").strip()
                        if line_str.startswith("data: "):
                            try:
                                data = json.loads(line_str[6:])
                                if data.get("type") == "content_block_delta":
                                    delta = data.get("delta", {})
                                    if delta.get("type") == "text_delta":
                                        yield delta.get("text", "")
                            except json.JSONDecodeError:
                                continue
        except Exception as e:
            yield f"[Error: {e}]"
