import os

from dotenv import load_dotenv

load_dotenv()


OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
ASSISTANT_NAME = os.getenv("ASSISTANT_NAME", "AI Assistant Manager")
BIN_DIR = os.getenv("BIN_DIR", "bin")
DATA_DIR = os.getenv("DATA_DIR", "data")
DATA_FILE_PREFIX = os.getenv("DATA_FILE_PREFIX", "AI Assistant Manager")
