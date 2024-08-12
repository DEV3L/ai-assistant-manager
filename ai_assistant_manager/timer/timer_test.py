from unittest.mock import patch

from ai_assistant_manager.timer.timer import timer


def test_timer_decorator():
    """
    Test that the timer decorator logs the correct message when the decorated function is called.
    """

    @timer("Test function")
    def dummy_function():
        pass

    with patch("ai_assistant_manager.timer.timer.logger") as mock_logger:
        dummy_function()

    # Ensure the logger is called once with the expected message
    mock_logger.debug.assert_called_once()
    assert "Test function: completed in" in mock_logger.debug.call_args[0][0]
