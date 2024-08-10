import os

from dotenv import load_dotenv

load_dotenv()


OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

ASSISTANT_DESCRIPTION = os.getenv("ASSISTANT_DESCRIPTION", "AI Assistant Manager")
ASSISTANT_NAME = os.getenv("ASSISTANT_NAME", "AI Assistant Manager")
BIN_DIR = os.getenv("BIN_DIR", "bin")
DATA_DIR = os.getenv("DATA_DIR", "data")
DATA_FILE_PREFIX = os.getenv("DATA_FILE_PREFIX", "AI Assistant Manager")


def reset_env_variables(env_file_path: str):
    global OPENAI_MODEL
    global ASSISTANT_DESCRIPTION
    global ASSISTANT_NAME
    global BIN_DIR
    global DATA_DIR
    global DATA_FILE_PREFIX

    load_dotenv(env_file_path, override=True)

    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

    ASSISTANT_DESCRIPTION = os.getenv("ASSISTANT_DESCRIPTION", "AI Assistant Manager")
    ASSISTANT_NAME = os.getenv("ASSISTANT_NAME", "AI Assistant Manager")
    BIN_DIR = os.getenv("BIN_DIR", "bin")
    DATA_DIR = os.getenv("DATA_DIR", "data")
    DATA_FILE_PREFIX = os.getenv("DATA_FILE_PREFIX", "AI Assistant Manager")
