"""Base authentication handler."""

from __future__ import annotations

from loguru import logger
from abc import ABC, abstractmethod
from typing import Any, Optional

from uncertainAPI.browsers.base import BrowserBackend

class AuthHandler(ABC):
    """Abstract base class for authentication handlers.

    Subclass this to implement custom authentication logic for different
    auth mechanisms (basic auth, OAuth, tokens, etc.).
    """

    def __init__(self, credentials: Optional[dict[str, Any]] = None) -> None:
        """Initialize auth handler.

        Args:
            credentials: Optional credentials dictionary.
        """
        self.credentials = credentials or {}

    @abstractmethod
    async def authenticate(self, browser: BrowserBackend) -> bool:
        """Authenticate using the browser.

        Args:
            browser: Browser backend instance.

        Returns:
            True if authentication successful, False otherwise.

        Raises:
            AuthenticationError: If authentication fails critically.
        """
        ...

    @abstractmethod
    async def is_authenticated(self, browser: BrowserBackend) -> bool:
        """Check if already authenticated.

        Args:
            browser: Browser backend instance.

        Returns:
            True if authenticated, False otherwise.
        """
        ...

    def get_credentials(self) -> dict[str, Any]:
        """Get credentials for authentication.

        Returns:
            Credentials dictionary.
        """
        return self.credentials

    async def save_session(self, browser: BrowserBackend) -> dict[str, Any]:
        """Save authentication session (e.g., cookies).

        Args:
            browser: Browser backend instance.

        Returns:
            Session data dictionary.
        """
        cookies = await browser.get_cookies()
        logger.debug("auth.session.saved", extra={"cookies_count": len(cookies)})
        return {"cookies": cookies}

    async def restore_session(self, browser: BrowserBackend, session_data: dict[str, Any]) -> None:
        """Restore authentication session.

        Args:
            browser: Browser backend instance.
            session_data: Session data from save_session.
        """
        cookies = session_data.get("cookies", [])
        if cookies:
            await browser.set_cookies(cookies)
            logger.debug("auth.session.restored", extra={"cookies_count": len(cookies)})



