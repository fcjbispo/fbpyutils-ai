import pytest
from fbpyutils_ai.tools.http import basic_header, USER_AGENTS

DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0"
EXPECTED_CONTENT_TYPE = "application/json"

def test_basic_header_default_user_agent():
    """
    Tests that basic_header returns the default user agent when no argument is provided.
    """
    headers = basic_header()
    assert isinstance(headers, dict)
    assert headers.get("User-Agent") == DEFAULT_USER_AGENT
    assert headers.get("Content-Type") == EXPECTED_CONTENT_TYPE

def test_basic_header_explicit_default_user_agent():
    """
    Tests that basic_header returns the default user agent when random_user_agent is False.
    """
    headers = basic_header(random_user_agent=False)
    assert isinstance(headers, dict)
    assert headers.get("User-Agent") == DEFAULT_USER_AGENT
    assert headers.get("Content-Type") == EXPECTED_CONTENT_TYPE

def test_basic_header_random_user_agent():
    """
    Tests that basic_header returns a random user agent from the list when random_user_agent is True.
    """
    headers = basic_header(random_user_agent=True)
    assert isinstance(headers, dict)
    assert headers.get("User-Agent") in USER_AGENTS
    assert headers.get("Content-Type") == EXPECTED_CONTENT_TYPE

def test_basic_header_content_type_always_present():
    """
    Tests that the Content-Type header is always present and correct, regardless of the user agent choice.
    """
    headers_default = basic_header()
    headers_random = basic_header(random_user_agent=True)

    assert headers_default.get("Content-Type") == EXPECTED_CONTENT_TYPE
    assert headers_random.get("Content-Type") == EXPECTED_CONTENT_TYPE

def test_user_agents_list_not_empty():
    """
    Ensures the USER_AGENTS list is populated.
    """
    assert USER_AGENTS is not None
    assert len(USER_AGENTS) > 0