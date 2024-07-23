import os

from loguru import logger


def does_data_exist(file_path: str) -> bool:
    """
    Check if the data file exists at the given file path.

    This function is used to determine whether a specific data file is already present,
    which helps in deciding whether to create a new directory or not.

    :param file_path: The path to the data file.
    :return: True if the file exists, False otherwise.
    """
    return os.path.exists(file_path)


def create_dir(dir_path: str, file_path: str):
    """
    Create a directory if the data file does not exist.

    This function ensures that the directory structure is in place before any data files are created.
    It prevents redundant directory creation if the data file already exists.

    :param dir_path: The path to the directory to create.
    :param file_path: The path to the data file to check.
    """
    if not does_data_exist(file_path):
        logger.info(f"Creating data dir path: {dir_path}")
        os.makedirs(dir_path, exist_ok=True)
