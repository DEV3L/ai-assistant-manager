import os
import shutil

from loguru import logger

from ai_assistant_manager.env_variables import ENV_VARIABLES
from ai_assistant_manager.exporters.exporter import (
    create_dir,
    does_data_exist,
)


class FilesExporter:
    """
    A class to handle exporting files to a specified directory.

    This class ensures that files are only exported if they do not already exist,
    and it manages the creation of necessary directories.
    """

    def __init__(
        self,
        file_name: str,
        *,
        directory: str = "files",
        bin_dir: str | None = None,
        data_dir: str | None = None,
        data_file_prefix: str | None = None,
    ) -> None:
        """
        Initialize the FilesExporter with file and directory information.

        :param file_name: The name of the file to export.
        :param directory: The target directory for the export (default is "files").
        :param bin_dir: The base directory for binaries (default is from environment variables).
        :param data_dir: The base directory for data files (default is from environment variables).
        :param data_file_prefix: The prefix for data files (default is from environment variables).
        """

        self.file_name = file_name
        self.directory = directory
        self.bin_dir = bin_dir if bin_dir else ENV_VARIABLES.bin_dir
        self.data_dir = data_dir if data_dir else ENV_VARIABLES.data_dir
        self.data_file_prefix = data_file_prefix if data_file_prefix else ENV_VARIABLES.data_file_prefix

    def export(self):
        """
        Export the file to the target directory if it does not already exist.

        This method checks for the existence of the file and skips the export if the file is already present.
        It also ensures that the necessary directory structure is created before writing the data.
        """
        if does_data_exist(self.get_file_path()):
            logger.info(f"{self._get_file_name_without_extension()} data exists. Skipping export.")
            return

        logger.info(f"Exporting {self._get_file_name_without_extension()} data")
        create_dir(self.get_dir_path(), self.get_file_path())
        self.write_data()

    def write_data(self):
        """
        Write the data to the target file path.

        This method copies the source file to the target file path and logs the operation.
        """
        source_path = os.path.join(self.data_dir, self.directory, self.file_name)
        shutil.copy(source_path, self.get_file_path())

        logger.info(f"{self._get_file_name_without_extension()} data written to file: {self.get_file_path()}")

    def get_dir_path(self):
        """
        Get the path to the target directory.

        :return: The path to the target directory.
        """
        return os.path.join(
            self.bin_dir,
            self.directory,
        )

    def get_file_path(self):
        """
        Get the full path to the target file.

        :return: The full path to the target file.
        """
        return os.path.join(
            self.get_dir_path(),
            f"{self.data_file_prefix} - {self.file_name}",
        )

    def _get_file_name_without_extension(self) -> str:
        """
        Get the file name without its extension.

        This method is used to log the file name without its extension for clarity.

        :return: The file name without its extension.
        """
        file_name_parts = os.path.basename(self.file_name)
        return os.path.splitext(file_name_parts)[0]
