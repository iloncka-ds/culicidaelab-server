"""
Tests for the LocaleSelector component.
"""

from unittest.mock import MagicMock, patch
import sys
from pathlib import Path

# Add frontend to path
frontend_path = Path(__file__).parent.parent.parent.parent / "frontend"
sys.path.insert(0, str(frontend_path))

with patch.dict(
    "sys.modules",
    {
        "solara": MagicMock(),
        "i18n": MagicMock(),
    },
):
    from frontend.components.common import locale_selector


def test_locale_selector_imports():
    """Test that locale selector module imports successfully."""
    assert locale_selector.LocaleSelector is not None
    assert callable(locale_selector.LocaleSelector)


def test_set_locale_function_exists():
    """Test that set_locale function exists."""
    assert hasattr(locale_selector, 'set_locale')
    assert callable(locale_selector.set_locale)


def test_locale_selector_dependencies():
    """Test that LocaleSelector has required dependencies."""
    assert hasattr(locale_selector, 'solara')
    assert hasattr(locale_selector, 'i18n')
    assert hasattr(locale_selector, 'LOCALES')
    assert isinstance(locale_selector.LOCALES, dict)


def test_locale_constants():
    """Test that locale constants are properly defined."""
    assert "ru" in locale_selector.LOCALES
    assert "en" in locale_selector.LOCALES
    assert locale_selector.LOCALES["ru"] == "Русский"
    assert locale_selector.LOCALES["en"] == "English"
