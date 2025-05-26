import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass
class EnvVariables:
    assistant_description: str
    assistant_name: str
    bin_dir: str
    data_dir: str
    data_file_prefix: str
    openai_model: str


def set_env_variables(env_file_path: str | None = None):
    global ENV_VARIABLES

    load_dotenv(env_file_path, override=True)

    ENV_VARIABLES.assistant_description = os.getenv("ASSISTANT_DESCRIPTION", "AI Assistant Manager")
    ENV_VARIABLES.assistant_name = os.getenv("ASSISTANT_NAME", "AI Assistant Manager")
    ENV_VARIABLES.bin_dir = os.getenv("BIN_DIR", "bin")
    ENV_VARIABLES.data_dir = os.getenv("DATA_DIR", "data")
    ENV_VARIABLES.data_file_prefix = os.getenv("DATA_FILE_PREFIX", "AI Assistant Manager")
    ENV_VARIABLES.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o")


# Initialize the global ENV_VARIABLES instance with default values or values from the environment
ENV_VARIABLES = EnvVariables(
    assistant_description=os.getenv("ASSISTANT_DESCRIPTION", "AI Assistant Manager"),
    assistant_name=os.getenv("ASSISTANT_NAME", "AI Assistant Manager"),
    bin_dir=os.getenv("BIN_DIR", "bin"),
    data_dir=os.getenv("DATA_DIR", "data"),
    data_file_prefix=os.getenv("DATA_FILE_PREFIX", "AI Assistant Manager"),
    openai_model=os.getenv("OPENAI_MODEL", "gpt-4o"),
)
