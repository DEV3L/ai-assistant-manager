from unittest.mock import Mock, patch

from .exporter import create_dir, does_data_exist


def test_does_data_exist():
    file_path = Mock(return_value="path/to/file")

    with patch("os.path.exists", return_value=True):
        result = does_data_exist(file_path)

    assert result


@patch("ai_assistant_manager.exporters.exporter.does_data_exist")
def test_create_dir_data_exists(mock_does_data_exist: Mock):
    mock_does_data_exist.return_value = True

    with patch("os.makedirs") as mock_makedirs:
        create_dir("dir/path", "file/path")

    mock_makedirs.assert_not_called()


@patch("ai_assistant_manager.exporters.exporter.does_data_exist")
def test_create_dir_data_does_not_exist(mock_does_data_exist: Mock):
    mock_does_data_exist.return_value = False

    with patch("os.makedirs") as mock_makedirs:
        create_dir("dir/path", "file/path")

    mock_makedirs.assert_called_once_with("dir/path", exist_ok=True)
