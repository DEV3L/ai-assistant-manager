from unittest.mock import patch

from src.timer.timer import timer


def test_timer_decorator():
    @timer("Test function")
    def dummy_function():
        pass

    with patch("src.timer.timer.logger") as mock_logger:
        dummy_function()

    mock_logger.debug.assert_called_once()
    assert "Test function: completed in" in mock_logger.debug.call_args[0][0]
