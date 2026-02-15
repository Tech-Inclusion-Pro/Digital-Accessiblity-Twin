"""GPT4All local AI client (direct Python library)."""

from typing import AsyncGenerator

from ai.prompts import SYSTEM_PROMPT_STUB


class GPT4AllClient:
    def __init__(self, model: str = "Meta-Llama-3-8B-Instruct.Q4_0.gguf"):
        self.model_name = model
        self._model = None

    def _ensure_model(self):
        if self._model is None:
            from gpt4all import GPT4All
            self._model = GPT4All(self.model_name)

    async def test_connection(self) -> tuple:
        try:
            self._ensure_model()
            return True, f"GPT4All loaded: {self.model_name}"
        except Exception as e:
            return False, f"Failed to load model: {e}"

    async def generate(self, user_message: str,
                       context: dict = None,
                       system_prompt: str = None,
                       conversation_history: list = None) -> AsyncGenerator[str, None]:
        try:
            self._ensure_model()
            sys_msg = system_prompt or SYSTEM_PROMPT_STUB
            # Build a single prompt incorporating history for GPT4All
            prompt_parts = []
            if conversation_history:
                for msg in conversation_history:
                    role = msg.get("role", "user")
                    prompt_parts.append(f"{role}: {msg.get('content', '')}")
            prompt_parts.append(f"user: {user_message}")
            full_prompt = "\n".join(prompt_parts)

            with self._model.chat_session(system_prompt=sys_msg):
                for token in self._model.generate(full_prompt, streaming=True):
                    yield token
        except Exception as e:
            yield f"[Error: {e}]"
