"""
Tests for the LocaleSelector component.
"""

from unittest.mock import MagicMock, patch
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "frontend"))

with patch.dict(
    "sys.modules",
    {
        "solara": MagicMock(),
        "i18n": MagicMock(),
    },
):
    from components.common import locale_selector


def test_get_current_locale():
    """Test that get_current_locale returns the current locale from i18n."""
    locale_selector.i18n.get.return_value = "en"

    result = locale_selector.get_current_locale()

    assert result == "en"
    locale_selector.i18n.get.assert_called_once_with("locale")


def test_set_locale():
    """Test that set_locale updates the locale in i18n."""
    test_locale = "ru"

    locale_selector.set_locale(test_locale)

    locale_selector.i18n.set.assert_called_once_with("locale", "ru")


@patch("components.common.locale_selector.solara")
@patch("components.common.locale_selector.i18n")
def test_locale_selector_initialization(mock_i18n, mock_solara):
    """Test that LocaleSelector initializes with the current locale."""
    mock_i18n.get.return_value = "en"
    mock_use_reactive = MagicMock()
    mock_use_reactive.return_value = mock_use_reactive
    mock_use_reactive.value = "en"
    mock_solara.use_reactive = mock_use_reactive

    locale_selector.LocaleSelector()

    mock_use_reactive.assert_called_once_with("en")


@patch("components.common.locale_selector.solara")
@patch("components.common.locale_selector.i18n")
def test_locale_selector_on_change(mock_i18n, mock_solara):
    """Test that changing the locale updates the i18n locale."""
    mock_i18n.get.return_value = "en"
    mock_use_reactive = MagicMock()
    reactive_obj = MagicMock()
    reactive_obj.value = "en"
    mock_use_reactive.return_value = reactive_obj
    mock_solara.use_reactive = mock_use_reactive

    mock_select = MagicMock()
    mock_solara.Select = mock_select

    locale_selector.LocaleSelector()

    on_value_callback = mock_select.call_args[1]["on_value"]

    on_value_callback("ru")

    mock_i18n.set.assert_called_once_with("locale", "ru")
    reactive_obj.set.assert_called_once_with("ru")
