"""Test basic package functionality."""

import uncertainAPI

def test_version_exists() -> None:
    """Test that the version attribute exists."""
    assert hasattr(uncertainAPI, "__version__")
    assert isinstance(uncertainAPI.__version__, str)
    assert len(uncertainAPI.__version__) > 0
