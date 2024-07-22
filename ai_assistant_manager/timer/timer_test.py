from unittest.mock import patch

from ai_assistant_manager.timer.timer import timer


def test_timer_decorator():
    @timer("Test function")
    def dummy_function():
        pass

    with patch("ai_assistant_manager.timer.timer.logger") as mock_logger:
        dummy_function()

    mock_logger.debug.assert_called_once()
    assert "Test function: completed in" in mock_logger.debug.call_args[0][0]
