from unittest.mock import Mock, patch

import pytest

from ai_assistant_manager.env_variables import BIN_DIR, DATA_DIR, DATA_FILE_PREFIX
from ai_assistant_manager.exporters.files.files_exporter import FilesExporter

FILE_NAME = "test_file.txt"
DATA_DIRECTORY = "test_dir"


@pytest.fixture(name="exporter")
def build_exporter():
    return FilesExporter(FILE_NAME, directory=DATA_DIRECTORY)


@patch("ai_assistant_manager.exporters.files.files_exporter.create_dir")
@patch("ai_assistant_manager.exporters.files.files_exporter.does_data_exist")
def test_export_data_exists(mock_does_data_exist, mock_create_dir, exporter):
    mock_does_data_exist.return_value = True

    exporter.export()

    mock_create_dir.assert_not_called()


@patch("ai_assistant_manager.exporters.files.files_exporter.create_dir")
@patch("ai_assistant_manager.exporters.files.files_exporter.does_data_exist")
def test_export_data_does_not_exist(mock_does_data_exist, mock_create_dir, exporter):
    mock_does_data_exist.return_value = False

    exporter.write_data = Mock()

    exporter.export()

    mock_create_dir.assert_called_once()
    exporter.write_data.assert_called_once()


@patch("ai_assistant_manager.exporters.files.files_exporter.shutil")
def test_write_data(mock_shutil, exporter):
    exporter.get_file_path = Mock(return_value="path/to/file")

    exporter.write_data()

    mock_shutil.copy.assert_called_once_with(f"{DATA_DIR}/{DATA_DIRECTORY}/{FILE_NAME}", "path/to/file")


def test_get_dir_path(exporter):
    result = exporter.get_dir_path()

    assert result == f"{BIN_DIR}/{DATA_DIRECTORY}"


def test_get_file_path(exporter):
    result = exporter.get_file_path()

    assert result == f"{BIN_DIR}/{DATA_DIRECTORY}/{DATA_FILE_PREFIX}_{FILE_NAME}"
