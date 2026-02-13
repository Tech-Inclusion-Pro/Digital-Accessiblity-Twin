"""AI backend connection test mocks."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock


@pytest.mark.asyncio
async def test_ollama_connection_success():
    from ai.ollama_client import OllamaClient
    client = OllamaClient()

    mock_resp = AsyncMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value={
        "models": [{"name": "gemma3:4b"}, {"name": "llama3:8b"}]
    })
    mock_resp.__aenter__ = AsyncMock(return_value=mock_resp)
    mock_resp.__aexit__ = AsyncMock(return_value=False)

    mock_session = AsyncMock()
    mock_session.get = MagicMock(return_value=mock_resp)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)

    with patch("aiohttp.ClientSession", return_value=mock_session):
        ok, msg = await client.test_connection()
        assert ok
        assert "gemma3:4b" in msg


@pytest.mark.asyncio
async def test_ollama_connection_failure():
    from ai.ollama_client import OllamaClient
    client = OllamaClient()

    with patch("aiohttp.ClientSession") as mock_cls:
        mock_cls.side_effect = Exception("Connection refused")
        ok, msg = await client.test_connection()
        assert not ok
        assert "Connection" in msg


@pytest.mark.asyncio
async def test_lmstudio_connection():
    from ai.lmstudio_client import LMStudioClient
    client = LMStudioClient()

    mock_resp = AsyncMock()
    mock_resp.status = 200
    mock_resp.__aenter__ = AsyncMock(return_value=mock_resp)
    mock_resp.__aexit__ = AsyncMock(return_value=False)

    mock_session = AsyncMock()
    mock_session.get = MagicMock(return_value=mock_resp)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)

    with patch("aiohttp.ClientSession", return_value=mock_session):
        ok, msg = await client.test_connection()
        assert ok


@pytest.mark.asyncio
async def test_cloud_openai_connection():
    from ai.cloud_client import CloudClient
    client = CloudClient("openai", "gpt-4o", "sk-test-key")

    mock_resp = AsyncMock()
    mock_resp.status = 200
    mock_resp.__aenter__ = AsyncMock(return_value=mock_resp)
    mock_resp.__aexit__ = AsyncMock(return_value=False)

    mock_session = AsyncMock()
    mock_session.get = MagicMock(return_value=mock_resp)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)

    with patch("aiohttp.ClientSession", return_value=mock_session):
        ok, msg = await client.test_connection()
        assert ok
        assert "OpenAI" in msg


@pytest.mark.asyncio
async def test_cloud_anthropic_key_format():
    from ai.cloud_client import CloudClient
    client = CloudClient("anthropic", "claude-sonnet-4-5-20250929", "sk-ant-test123")
    ok, msg = await client.test_connection()
    assert ok

    bad_client = CloudClient("anthropic", "claude-sonnet-4-5-20250929", "invalid-key")
    ok, msg = await bad_client.test_connection()
    assert not ok


@pytest.mark.asyncio
async def test_backend_manager_no_client():
    from ai.backend_manager import BackendManager
    bm = BackendManager()
    bm._client = None
    chunks = []
    async for chunk in bm.generate_response("hello"):
        chunks.append(chunk)
    assert any("No AI backend" in c for c in chunks)
