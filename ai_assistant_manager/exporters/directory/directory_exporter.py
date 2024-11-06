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
    def __init__(self, directory: str):
        self.directory = directory

    def export(self):
        if does_data_exist(self.get_file_path()):
            logger.info(f"Directory '{self.directory}' data exists. Skipping export.")
            return

        logger.info(f"Exporting directory '{self.directory}' data")
        create_dir(self.get_dir_path(), self.get_file_path())
        self.write_data()

    def write_data(self):
        data = self.load()
        data_as_dicts = {data.title: asdict(data) for data in data}
        json_data = json.dumps(data_as_dicts)

        with open(self.get_file_path(), "w", encoding=UTF_8) as file:
            file.write(json_data)

        logger.info(f"Directory '{self.directory}' data written to file: {self.get_file_path()}")

    def load(self):
        files = os.listdir(self.get_data_dir_path())
        return [self.file_load(filename) for filename in files]

    def file_load(self, filename: str) -> ContentData:
        file_id = filename[:3]
        name, _ = os.path.splitext(filename)
        title = name[3:].strip()

        with open(os.path.join(self.get_data_dir_path(), filename), "r", encoding=UTF_8) as file:
            lines = file.readlines()

        body = "\n".join([line.strip() for line in lines[1:]])
        date = parser.parse(lines[0].strip()).isoformat()

        return ContentData(id=file_id, title=title, body=body, date=date)

    def get_dir_path(self) -> str:
        return os.path.join(ENV_VARIABLES.bin_dir, self.directory)

    def get_file_path(self) -> str:
        return os.path.join(self.get_dir_path(), f"{ENV_VARIABLES.data_file_prefix} - {self.directory}.json")

    def get_data_dir_path(self) -> str:
        return os.path.join(ENV_VARIABLES.data_dir, self.directory)
