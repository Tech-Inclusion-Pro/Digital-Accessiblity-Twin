"""Ollama local AI client."""

import json
from typing import AsyncGenerator

import aiohttp

from ai.prompts import SYSTEM_PROMPT_STUB


class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "gemma3:4b"):
        self.base_url = base_url.rstrip("/")
        self.model = model

    async def test_connection(self) -> tuple:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/api/tags",
                    timeout=aiohttp.ClientTimeout(total=5),
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        models = [m["name"] for m in data.get("models", [])]
                        return True, f"Connected. Models: {', '.join(models[:5])}"
                    return False, f"Server returned status {resp.status}"
        except Exception as e:
            return False, f"Connection failed: {e}"

    async def list_models(self) -> list:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/api/tags",
                    timeout=aiohttp.ClientTimeout(total=5),
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return [m["name"] for m in data.get("models", [])]
        except Exception:
            pass
        return []

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
                    f"{self.base_url}/api/chat",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=120),
                ) as resp:
                    if resp.status != 200:
                        yield f"Error: {await resp.text()}"
                        return
                    async for line in resp.content:
                        if line:
                            try:
                                data = json.loads(line.decode("utf-8"))
                                chunk = data.get("message", {}).get("content", "")
                                if chunk:
                                    yield chunk
                            except json.JSONDecodeError:
                                continue
        except Exception as e:
            yield f"[Error: {e}]"
