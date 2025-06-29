"""
Pytest configuration for frontend tests.
"""
import pytest
from pathlib import Path


@pytest.fixture(scope="session")
def frontend_root():
    """Return the path to the frontend directory."""
    return Path(__file__).parent.parent / "frontend"
