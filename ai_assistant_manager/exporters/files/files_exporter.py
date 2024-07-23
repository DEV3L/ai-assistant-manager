import os
import shutil

from loguru import logger

from ai_assistant_manager.env_variables import BIN_DIR, DATA_DIR, DATA_FILE_PREFIX
from ai_assistant_manager.exporters.exporter import (
    create_dir,
    does_data_exist,
)


class FilesExporter:
    def __init__(
        self,
        file_name: str,
        *,
        directory: str = "files",
        bin_dir: str = BIN_DIR,
        data_dir: str = DATA_DIR,
        data_file_prefix: str = DATA_FILE_PREFIX,
    ) -> None:
        self.file_name = file_name
        self.directory = directory
        self.bin_dir = bin_dir
        self.data_dir = data_dir
        self.data_file_prefix = data_file_prefix

    def export(self):
        if does_data_exist(self.get_file_path()):
            logger.info(f"{self._get_file_name_without_extension()} data exits. Skipping export.")
            return

        logger.info(f"Exporting {self._get_file_name_without_extension()} data")
        create_dir(self.get_dir_path(), self.get_file_path())
        self.write_data()

    def write_data(self):
        source_path = os.path.join(self.data_dir, self.directory, self.file_name)
        shutil.copy(source_path, self.get_file_path())

        logger.info(f"{self._get_file_name_without_extension()} data written to file: {self.get_file_path()}")

    def get_dir_path(self):
        return os.path.join(
            self.bin_dir,
            self.directory,
        )

    def get_file_path(self):
        return os.path.join(
            self.get_dir_path(),
            f"{self.data_file_prefix}_{self.file_name}",
        )

    def _get_file_name_without_extension(self) -> str:
        file_name_parts = os.path.basename(self.file_name)
        return os.path.splitext(file_name_parts)[0]
