"""AI backend manager — facade over local and cloud clients."""

import asyncio
from typing import AsyncGenerator


class BackendManager:
    """Unified facade for AI backend configuration and usage."""

    def __init__(self):
        self.provider_type = "local"   # "local" or "cloud"
        self.provider = "ollama"       # ollama, lmstudio, gpt4all, openai, anthropic
        self.model = "gemma3:4b"
        self.api_key = None
        self.base_url = "http://localhost:11434"
        self.cloud_consent_institutional = False
        self.cloud_consent_data = False
        self._client = None

    def configure(self, provider_type: str, provider: str, model: str = None,
                  api_key: str = None, base_url: str = None):
        self.provider_type = provider_type
        self.provider = provider
        if model:
            self.model = model
        if api_key:
            self.api_key = api_key
        if base_url:
            self.base_url = base_url
        self._client = self._make_client()

    def _make_client(self):
        if self.provider_type == "local":
            if self.provider == "ollama":
                from ai.ollama_client import OllamaClient
                return OllamaClient(self.base_url, self.model)
            elif self.provider == "lmstudio":
                from ai.lmstudio_client import LMStudioClient
                return LMStudioClient(self.base_url, self.model)
            elif self.provider == "gpt4all":
                from ai.gpt4all_client import GPT4AllClient
                return GPT4AllClient(self.model)
        else:
            from ai.cloud_client import CloudClient
            return CloudClient(self.provider, self.model, self.api_key)
        return None

    @property
    def cloud_consent_granted(self) -> bool:
        return self.cloud_consent_institutional and self.cloud_consent_data

    async def test_connection(self) -> tuple:
        if self._client is None:
            self._client = self._make_client()
        if self._client is None:
            return False, "No client configured"
        return await self._client.test_connection()

    async def generate_response(self, user_message: str,
                                context: dict = None) -> AsyncGenerator[str, None]:
        if self._client is None:
            yield "No AI backend configured."
            return
        async for chunk in self._client.generate(user_message, context):
            yield chunk
