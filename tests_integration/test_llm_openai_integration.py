import pytest
import os
from unittest.mock import patch
import requests

from fbpyutils_ai.tools.llm import LLMServiceTool

@pytest.fixture
def openai_service():
    api_base = os.environ['FBPY_OPENAI_API_BASE_URL']
    embedding_api_base = os.environ['FBPY_OPENAI_API_BASE_URL']
    api_key = os.environ['FBPY_OPENAI_API_KEY']
    llm_model = os.environ['FBPY_LLM_CHAT_MODEL']
    embedding_model = os.environ['FBPY_LLM_EMBEDDING_MODEL']
    return LLMServiceTool(
        api_base=api_base,
        api_embed_base=embedding_api_base,
        api_key=api_key,
        model_id=llm_model,
        embed_model=embedding_model,
        timeout=10,
        session_retries=2
    )

@pytest.fixture
def openai_service_same_base():
    api_base = os.environ['FBPY_OPENAI_API_BASE_URL']
    api_key = os.environ['FBPY_OPENAI_API_KEY']
    llm_model = os.environ['FBPY_LLM_CHAT_MODEL']
    embedding_model = os.environ['FBPY_LLM_EMBEDDING_MODEL']
    return LLMServiceTool(
        api_base=api_base,
        api_embed_base=api_base,
        api_key=api_key,
        model_id=llm_model,
        embed_model=embedding_model,
        timeout=5,
        session_retries=2,
    )

def test_generate_embedding(openai_service):
    embedding = openai_service.generate_embedding("Test text")
    assert isinstance(embedding, list)
    assert len(embedding) > 0

def test_generate_text(openai_service):
    text = openai_service.generate_text("Test prompt")
    assert isinstance(text, str)
    assert len(text) > 0

def test_generate_completions(openai_service):
    messages = [{"role": "user", "content": "Test message"}]
    completion = openai_service.generate_completions(messages)
    assert isinstance(completion, str)
    assert len(completion) > 0

def test_generate_completions_streaming(openai_service):
    messages = [{"role": "user", "content": "Test message"}]
    completion_generator = openai_service.generate_completions(messages, stream=True)
    
    # Verify it's a generator
    from types import GeneratorType
    assert isinstance(completion_generator, GeneratorType)
    
    # Collect all chunks
    chunks = []
    for chunk in completion_generator:
        chunks.append(chunk)
    
    # Should have at least one chunk
    assert len(chunks) > 0
    # Each chunk should be a string
    assert all(isinstance(chunk, str) for chunk in chunks)

def test_timeout_resilience(openai_service):
    with patch('requests.Session.post') as mock_post:
        mock_post.side_effect = requests.exceptions.Timeout()
        with pytest.raises(requests.exceptions.Timeout):
            openai_service.generate_text("This is a test prompt")
        assert mock_post.call_count == 1

def test_generate_embedding_same_base(openai_service_same_base):
    embedding = openai_service_same_base.generate_embedding("Test text")
    assert isinstance(embedding, list)
    assert len(embedding) > 0

def test_generate_text_same_base(openai_service_same_base):
    text = openai_service_same_base.generate_text("Test prompt")
    assert isinstance(text, str)
    assert len(text) > 0
