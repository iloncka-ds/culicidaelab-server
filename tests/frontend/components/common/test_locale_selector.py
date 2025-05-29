"""
Tests for the LocaleSelector component.
"""
import pytest
from unittest.mock import MagicMock, patch
import sys
from pathlib import Path

# Import the component to test
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "frontend"))

# Mock the solara and i18n modules before importing the component
with patch.dict('sys.modules', {
    'solara': MagicMock(),
    'i18n': MagicMock(),
}):
    from components.common import locale_selector

def test_get_current_locale():
    """Test that get_current_locale returns the current locale from i18n."""
    # Setup
    locale_selector.i18n.get.return_value = "en"
    
    # Test
    result = locale_selector.get_current_locale()
    
    # Assert
    assert result == "en"
    locale_selector.i18n.get.assert_called_once_with("locale")

def test_set_locale():
    """Test that set_locale updates the locale in i18n."""
    # Setup
    test_locale = "ru"
    
    # Test
    locale_selector.set_locale(test_locale)
    
    # Assert
    locale_selector.i18n.set.assert_called_once_with("locale", "ru")

@patch('components.common.locale_selector.solara')
@patch('components.common.locale_selector.i18n')
def test_locale_selector_initialization(mock_i18n, mock_solara):
    """Test that LocaleSelector initializes with the current locale."""
    # Setup
    mock_i18n.get.return_value = "en"
    mock_use_reactive = MagicMock()
    mock_use_reactive.return_value = mock_use_reactive
    mock_use_reactive.value = "en"
    mock_solara.use_reactive = mock_use_reactive
    
    # Create the component
    locale_selector.LocaleSelector()
    
    # Assert
    mock_use_reactive.assert_called_once_with("en")

@patch('components.common.locale_selector.solara')
@patch('components.common.locale_selector.i18n')
def test_locale_selector_on_change(mock_i18n, mock_solara):
    """Test that changing the locale updates the i18n locale."""
    # Setup
    mock_i18n.get.return_value = "en"
    mock_use_reactive = MagicMock()
    reactive_obj = MagicMock()
    reactive_obj.value = "en"
    mock_use_reactive.return_value = reactive_obj
    mock_solara.use_reactive = mock_use_reactive
    
    # Mock the Select component
    mock_select = MagicMock()
    mock_solara.Select = mock_select
    
    # Create the component
    locale_selector.LocaleSelector()
    
    # Get the on_value callback
    on_value_callback = mock_select.call_args[1]["on_value"]
    
    # Call the callback with a new locale
    on_value_callback("ru")
    
    # Assert that the locale was updated
    mock_i18n.set.assert_called_once_with("locale", "ru")
    reactive_obj.set.assert_called_once_with("ru")
