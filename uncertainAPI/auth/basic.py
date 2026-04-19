"""Basic authentication handler."""

from __future__ import annotations

from loguru import logger
from typing import Any, Optional

from uncertainAPI.auth.base import AuthHandler
from uncertainAPI.browsers.base import BrowserBackend
from uncertainAPI.exceptions import AuthenticationError

class BasicAuthHandler(AuthHandler):
    """Handler for basic username/password authentication.

    Supports form-based login with configurable selectors.
    """

    def __init__(
        self,
        credentials: Optional[dict[str, Any]] = None,
        username_selector: str = "input[name='username']",
        password_selector: str = "input[name='password']",
        submit_selector: str = "button[type='submit']",
        success_indicator: Optional[str] = None,
    ) -> None:
        """Initialize basic auth handler.

        Args:
            credentials: Dict with 'username' and 'password' keys.
            username_selector: CSS selector for username input.
            password_selector: CSS selector for password input.
            submit_selector: CSS selector for submit button.
            success_indicator: CSS selector that appears after successful login.
        """
        super().__init__(credentials)
        self.username_selector = username_selector
        self.password_selector = password_selector
        self.submit_selector = submit_selector
        self.success_indicator = success_indicator

    async def authenticate(self, browser: BrowserBackend) -> bool:
        """Authenticate using username and password.

        Args:
            browser: Browser backend instance.

        Returns:
            True if authentication successful.

        Raises:
            AuthenticationError: If authentication fails.
        """
        username = self.credentials.get("username")
        password = self.credentials.get("password")

        if not username or not password:
            raise AuthenticationError("Username and password required for basic auth")

        logger.debug("auth.basic.start", extra={"username": username})

        try:
            # Fill in credentials
            await browser.fill(self.username_selector, username)
            await browser.fill(self.password_selector, password)

            # Submit form
            await browser.click(self.submit_selector)

            # Wait for success indicator if provided
            if self.success_indicator:
                await browser.wait_for_selector(self.success_indicator, timeout=10000)

            logger.info("auth.basic.success", extra={"username": username})
            return True

        except Exception as exc:
            logger.warning("auth.basic.failed", extra={"username": username, "error": str(exc)})
            raise AuthenticationError(f"Basic authentication failed: {exc}") from exc

    async def is_authenticated(self, browser: BrowserBackend) -> bool:
        """Check if already authenticated.

        Args:
            browser: Browser backend instance.

        Returns:
            True if authenticated (success indicator present).
        """
        if not self.success_indicator:
            # Can't verify without success indicator
            return False

        try:
            html = await browser.get_html()
            # Simple check - in production, use more robust detection
            return self.success_indicator in html
        except Exception as exc:
            logger.debug("auth.basic.check_failed", extra={"error": str(exc)})
            return False



