"""Tests for authentication handlers."""

from __future__ import annotations

import pytest

from uncertainAPI.auth.basic import BasicAuthHandler
from uncertainAPI.auth.token import TokenAuthHandler

class TestBasicAuthHandler:
    """Test basic authentication handler."""

    def test_init(self) -> None:
        """Test handler initialization."""
        credentials = {"username": "test", "password": "secret"}
        handler = BasicAuthHandler(credentials=credentials)

        assert handler.credentials == credentials
        assert handler.username_selector == "input[name='username']"

    def test_get_credentials(self) -> None:
        """Test getting credentials."""
        credentials = {"username": "test", "password": "secret"}
        handler = BasicAuthHandler(credentials=credentials)

        result = handler.get_credentials()
        assert result == credentials

class TestTokenAuthHandler:
    """Test token authentication handler."""

    def test_init(self) -> None:
        """Test handler initialization."""
        credentials = {"token": "test-token-123"}
        handler = TokenAuthHandler(credentials=credentials)

        assert handler.credentials == credentials
        assert handler.token_key == "token"

    def test_custom_token_key(self) -> None:
        """Test custom token key."""
        credentials = {"api_key": "test-key"}
        handler = TokenAuthHandler(
            credentials=credentials,
            token_key="api_key",
        )

        assert handler.token_key == "api_key"



