# AI Assistant Manager

This repository provides tools and services to manage OpenAI Assistants, including creating, listing, and deleting assistants, as well as handling vector stores and retrieval files. It includes end-to-end and unit tests, and leverages the Hatch build system for environment management and testing.

## Install through PyPI

```bash
pip install ai-assistant-manager
```

For more details, visit the [PyPI project page](https://pypi.org/project/ai-assistant-manager/).

## Setup

1. Clone the repository:

```bash
git clone https://github.com/DEV3L/ai-assistant-manager
cd ai-assistant-manager
```

2. Copy the env.local file to a new file named .env and replace `OPENAI_API_KEY` with your actual OpenAI API key:

```bash
cp env.local .env
```

3. Setup a virtual environment with dependencies and activate it:

```bash
brew install hatch
hatch env create
hatch shell
```

## Environment Variables

The following environment variables can be configured in the `.env` file:

- `OPENAI_MODEL`: The model to use (default: `gpt-4o-2024-08-06`)
- `ASSISTANT_DESCRIPTION`: Description of the assistant (default: `AI Assistant Manager`)
- `ASSISTANT_NAME`: Name of the assistant (default: `AI Assistant Manager`)
- `BIN_DIR`: Directory for binaries (default: `bin`)
- `DATA_DIR`: Directory for data files (default: `data`)
- `DATA_FILE_PREFIX`: Prefix for data files (default: `AI Assistant Manager`)

## Testing

### End to End Test

```bash
hatch run e2e
```

### Unit Tests

```bash
hatch run test
```

### Coverage Gutters:

```bash
Command + Shift + P => Coverage Gutters: Watch
```

## Example

```
from loguru import logger

from ai_assistant_manager.assistants.assistant_service import (
    AssistantService,
)
from ai_assistant_manager.chats.chat import Chat
from ai_assistant_manager.clients.openai_api import OpenAIClient, build_openai_client
from ai_assistant_manager.env_variables import set_env_variables
from ai_assistant_manager.exporters.directory.directory_exporter import DirectoryExporter
from ai_assistant_manager.exporters.files.files_exporter import FilesExporter
from ai_assistant_manager.prompts.prompt import get_prompt


def main():
    DirectoryExporter("directory").export()
    FilesExporter("about.txt").export()

    assistant_name = "AI-Assistant-Manager-Test"
    logger.info(f"Building {assistant_name}")

    client = OpenAIClient(build_openai_client())
    service = AssistantService(client, get_prompt())

    logger.info("Removing existing assistant and category files")
    service.delete_assistant()

    assistant_id = service.get_assistant_id()
    logger.info(f"Assistant ID: {assistant_id}")

    chat = Chat(client, assistant_id)
    chat.start()

    message = "What is the AI Assistant Manager?"
    print(f"\nMessage:\n{message}")

    chat_response = chat.send_user_message(message)
    print(f"\n{service.assistant_name}:\n{chat_response.message}")
    print(f"\nTokens: {chat_response.token_count}")

    // service.delete_assistant()


if __name__ == "__main__":
    try:
        set_env_variables()
        main()
    except Exception as e:
        logger.info(f"Error: {e}")
```

## Contributing

We welcome contributions! To contribute:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Make your changes.
4. Ensure all tests pass.
5. Submit a pull request with a detailed description of your changes.

## Code of Conduct

We expect all contributors to adhere to our Code of Conduct:

- Be respectful and considerate.
- Avoid discriminatory or offensive language.
- Report any unacceptable behavior to the project maintainers.

By participating in this project, you agree to abide by these guidelines.
