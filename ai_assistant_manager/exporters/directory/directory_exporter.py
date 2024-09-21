import json
import os
from dataclasses import asdict

from dateutil import parser
from loguru import logger

from ai_assistant_manager.encoding import UTF_8
from ai_assistant_manager.env_variables import ENV_VARIABLES

from ..content_data import ContentData
from ..exporter import create_dir, does_data_exist


class DirectoryExporter:
    """
    Handles exporting data from a directory to a JSON file.
    """

    def __init__(self, directory: str):
        """
        Initialize the DirectoryExporter with the target directory.

        :param directory: The directory to export data from.
        """
        self.directory = directory

    def export(self):
        """
        Export the directory data to a JSON file if it doesn't already exist.
        """
        if does_data_exist(self.get_file_path()):
            logger.info(f"Directory '{self.directory}' data exits. Skipping export.")
            return

        logger.info(f"Exporting directory '{self.directory}' data")
        create_dir(self.get_dir_path(), self.get_file_path())
        self.write_data()

    def write_data(self):
        """
        Write the loaded data to a JSON file.
        """
        data = self.load()

        data_as_dicts = {data.title: asdict(data) for data in data}
        json_data = json.dumps(data_as_dicts)

        with open(self.get_file_path(), "w", encoding=UTF_8) as file:
            file.write(json_data)

        logger.info(f"Directory '{self.directory}' data written to file: {self.get_file_path()}")

    def load(self):
        """
        Load data from files in the directory.

        :return: A list of ContentData objects.
        """
        files = os.listdir(self.get_data_dir_path())
        return [self.file_load(filename) for filename in files]

    def file_load(self, filename: str) -> ContentData:
        """
        Load data from a single file.

        :param filename: The name of the file to load.
        :return: A ContentData object with the file's data.
        """
        file_id = filename[:3]
        name, _ = os.path.splitext(filename)
        title = name[3:].strip()

        with open(
            os.path.join(self.get_data_dir_path(), filename),
            "r",
            encoding=UTF_8,
        ) as file:
            lines = file.readlines()

        body = "\n".join([line.strip() for line in lines[1:]])

        date = parser.parse(lines[0].strip()).isoformat()

        return ContentData(
            id=file_id,
            title=title,
            body=body,
            date=date,
        )

    def get_dir_path(self) -> str:
        """
        Get the path to the directory.

        :return: The directory path.
        """
        return os.path.join(
            ENV_VARIABLES.bin_dir,
            self.directory,
        )

    def get_file_path(self) -> str:
        """
        Get the path to the JSON file where data will be exported.

        :return: The file path.
        """
        return os.path.join(
            self.get_dir_path(),
            f"{ENV_VARIABLES.data_file_prefix} - {self.directory}.json",
        )

    def get_data_dir_path(self) -> str:
        """
        Get the path to the directory containing the data files.

        :return: The data directory path.
        """
        return os.path.join(ENV_VARIABLES.data_dir, self.directory)
