import os

from loguru import logger


def does_data_exist(file_path: str) -> bool:
    return os.path.exists(file_path)


def create_dir(dir_path: str, file_path: str):
    if not does_data_exist(file_path):
        logger.info(f"Creating data dir path: {dir_path}")
        os.makedirs(dir_path, exist_ok=True)
