"""Regression tests for the lightweight core import boundary."""

from __future__ import annotations

import subprocess
import sys


def test_core_import_does_not_load_optional_dependencies() -> None:
    """Importing the core/runtime must not import optional connector libraries."""

    code = (
        "import sys; "
        "import uncertainAPI; "
        "import uncertainAPI.core; "
        "import uncertainAPI.runtime; "
        "import uncertainAPI.adapters; "
        "assert 'httpx' not in sys.modules; "
        "assert 'jmespath' not in sys.modules; "
        "assert 'jsonschema' not in sys.modules; "
        "assert 'dlt' not in sys.modules"
    )
    subprocess.run([sys.executable, "-c", code], check=True)
