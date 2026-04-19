"""Token-based authentication handler."""

from __future__ import annotations

from loguru import logger
from typing import Any, Optional

from uncertainAPI.auth.base import AuthHandler
from uncertainAPI.browsers.base import BrowserBackend
from uncertainAPI.exceptions import AuthenticationError

class TokenAuthHandler(AuthHandler):
    """Handler for token-based authentication.

    Supports API tokens, JWT, and bearer token authentication.
    """

    def __init__(
        self,
        credentials: Optional[dict[str, Any]] = None,
        token_key: str = "token",
        header_name: str = "Authorization",
        token_prefix: str = "Bearer",
    ) -> None:
        """Initialize token auth handler.

        Args:
            credentials: Dict with token key.
            token_key: Key name for token in credentials.
            header_name: HTTP header name for token.
            token_prefix: Prefix for token value (e.g., 'Bearer', 'Token').
        """
        super().__init__(credentials)
        self.token_key = token_key
        self.header_name = header_name
        self.token_prefix = token_prefix

    async def authenticate(self, browser: BrowserBackend) -> bool:
        """Authenticate using token.

        Args:
            browser: Browser backend instance.

        Returns:
            True if authentication successful.

        Raises:
            AuthenticationError: If authentication fails.
        """
        token = self.credentials.get(self.token_key)

        if not token:
            raise AuthenticationError(f"Token required (key: {self.token_key})")

        logger.debug("auth.token.start")

        try:
            # Inject token via JavaScript (for browser-based APIs)
            # This sets the token in localStorage or sessionStorage
            script = f"""
            localStorage.setItem('{self.token_key}', '{token}');
            sessionStorage.setItem('{self.token_key}', '{token}');
            """
            await browser.execute_script(script)

            logger.info("auth.token.success")
            return True

        except Exception as exc:
            logger.warning("auth.token.failed", extra={"error": str(exc)})
            raise AuthenticationError(f"Token authentication failed: {exc}") from exc

    async def is_authenticated(self, browser: BrowserBackend) -> bool:
        """Check if already authenticated.

        Args:
            browser: Browser backend instance.

        Returns:
            True if token exists in storage.
        """
        try:
            script = f"return localStorage.getItem('{self.token_key}') || sessionStorage.getItem('{self.token_key}');"
            stored_token = await browser.execute_script(script)
            return bool(stored_token)
        except Exception as exc:
            logger.debug("auth.token.check_failed", extra={"error": str(exc)})
            return False



