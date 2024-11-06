import os
import shutil

from loguru import logger

from ai_assistant_manager.env_variables import ENV_VARIABLES

from ..exporter import create_dir, does_data_exist


class FilesExporter:
    def __init__(
        self,
        file_name: str,
        *,
        directory: str = "files",
        bin_dir: str | None = None,
        data_dir: str | None = None,
        data_file_prefix: str | None = None,
    ) -> None:
        self.file_name = file_name
        self.directory = directory
        self.bin_dir = bin_dir if bin_dir else ENV_VARIABLES.bin_dir
        self.data_dir = data_dir if data_dir else ENV_VARIABLES.data_dir
        self.data_file_prefix = data_file_prefix if data_file_prefix else ENV_VARIABLES.data_file_prefix

    def export(self):
        if does_data_exist(self.get_file_path()):
            logger.info(f"{self._get_file_name_without_extension()} data exists. Skipping export.")
            return

        logger.info(f"Exporting {self._get_file_name_without_extension()} data")
        create_dir(self.get_dir_path(), self.get_file_path())
        self.write_data()

    def write_data(self):
        source_path = os.path.join(self.data_dir, self.directory, self.file_name)
        shutil.copy(source_path, self.get_file_path())
        logger.info(f"{self._get_file_name_without_extension()} data written to file: {self.get_file_path()}")

    def get_dir_path(self) -> str:
        return os.path.join(self.bin_dir, self.directory)

    def get_file_path(self) -> str:
        return os.path.join(self.get_dir_path(), f"{self.data_file_prefix} - {self.file_name}")

    def _get_file_name_without_extension(self) -> str:
        file_name_parts = os.path.basename(self.file_name)
        return os.path.splitext(file_name_parts)[0]
