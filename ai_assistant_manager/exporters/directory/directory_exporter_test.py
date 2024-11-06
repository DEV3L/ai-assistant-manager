from unittest.mock import Mock, mock_open, patch

import pytest

from ai_assistant_manager.env_variables import ENV_VARIABLES

from ..content_data import ContentData
from .directory_exporter import DirectoryExporter

example_directory = "directory"


@pytest.fixture(name="exporter")
def build_exporter() -> DirectoryExporter:
    return DirectoryExporter(example_directory)


@patch("ai_assistant_manager.exporters.directory.directory_exporter.create_dir")
@patch("ai_assistant_manager.exporters.directory.directory_exporter.does_data_exist")
def test_export_data_exists(mock_does_data_exist: Mock, mock_create_dir: Mock, exporter: DirectoryExporter):
    mock_does_data_exist.return_value = True

    exporter.export()

    mock_create_dir.assert_not_called()


@patch("ai_assistant_manager.exporters.directory.directory_exporter.create_dir")
@patch("ai_assistant_manager.exporters.directory.directory_exporter.does_data_exist")
def test_export_data_does_not_exist(mock_does_data_exist: Mock, mock_create_dir: Mock, exporter: DirectoryExporter):
    mock_does_data_exist.return_value = False

    exporter.write_data = Mock()

    exporter.export()

    mock_create_dir.assert_called_once()
    exporter.write_data.assert_called_once()


@patch("builtins.open", new_callable=mock_open)
@patch("json.dumps")
def test_write_data(mock_json_dumps: Mock, mock_open_file: Mock, exporter: DirectoryExporter):
    exporter.load = Mock(return_value=[])
    mock_json_dumps.return_value = "{}"

    exporter.write_data()

    exporter.load.assert_called_once()
    mock_open_file.assert_called_once_with(exporter.get_file_path(), "w", encoding="utf-8")
    mock_open_file().write.assert_called_once_with(mock_json_dumps.return_value)


@patch("os.listdir")
def test_load(mock_listdir: Mock, exporter: DirectoryExporter):
    exporter.file_load = Mock(return_value=ContentData(id="1", title="Test", body="Test body", date="2022-01-01"))
    mock_listdir.return_value = ["01 We Call It Saw Time.txt"]

    result = exporter.load()

    assert len(result) == 1
    assert all(isinstance(item, ContentData) for item in result)


def test_file_load(exporter: DirectoryExporter):
    exporter.get_data_dir_path = Mock(return_value="data/directory")

    filename = "001 Test File.md"
    blog_data = exporter.file_load(filename)

    assert blog_data.id == "001"
    assert blog_data.title == "Test File"
    assert isinstance(blog_data.body, str)
    assert blog_data.date == "2024-08-12T00:00:00"


def test_get_dir_path(exporter: DirectoryExporter):
    result = exporter.get_dir_path()

    assert result == f"{ENV_VARIABLES.bin_dir}/{example_directory}"


def test_get_file_path(exporter: DirectoryExporter):
    result = exporter.get_file_path()

    assert (
        result
        == f"{ENV_VARIABLES.bin_dir}/{example_directory}/{ENV_VARIABLES.data_file_prefix} - {example_directory}.json"
    )


def test_get_data_dir_path(exporter: DirectoryExporter):
    result = exporter.get_data_dir_path()

    assert result == f"{ENV_VARIABLES.data_dir}/{example_directory}"
