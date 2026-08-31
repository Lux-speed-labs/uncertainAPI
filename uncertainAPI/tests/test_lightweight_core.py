"""Regression tests for the lightweight core import boundary."""

from __future__ import annotations

import subprocess
import sys


def test_core_import_does_not_load_optional_http_dependency() -> None:
    """Importing the core/runtime must not import httpx."""

    code = (
        "import sys; "
        "import uncertainAPI; "
        "import uncertainAPI.core; "
        "import uncertainAPI.runtime; "
        "assert 'httpx' not in sys.modules"
    )
    subprocess.run([sys.executable, "-c", code], check=True)
