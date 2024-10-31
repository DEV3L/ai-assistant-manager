# AI Assistant Manager

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ai-assistant-manager)
![PyPI version](https://img.shields.io/pypi/v/ai-assistant-manager)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
![Build Status](https://img.shields.io/github/actions/workflow/status/DEV3L/ai-assistant-manager/continuous-integration.yml?branch=main)
![Open Source Love](https://badges.frapsoft.com/os/v1/open-source.svg?v=103)

## Introduction

**AI Assistant Manager** is an **open-source** tool designed to simplify the management of OpenAI Assistants. It provides a suite of tools and services for creating, listing, and deleting assistants, as well as handling vector stores and retrieval files. The project includes both end-to-end and unit tests, leveraging the Hatch build system for environment management and testing.

## Value Proposition

By automating the management of AI assistants and their associated resources, **AI Assistant Manager** streamlines workflows for developers working with OpenAI's API. It reduces the complexity involved in assistant lifecycle management, vector store handling, and file operations, allowing developers to focus on building intelligent applications without getting bogged down in infrastructure details.

## Key Features

- **Assistant Management**: Create, list, and delete OpenAI assistants with ease.
- **Vector Store Handling**: Manage vector stores for retrieval-augmented generation (RAG) models.
- **Retrieval File Management**: Create and handle retrieval files efficiently.
- **Open Source**: Freely available for modification and integration.
- **Testing Suite**: Includes end-to-end and unit tests to ensure reliability.
- **Environment Management**: Utilizes Hatch for consistent development environments.
- **Logging**: Integrated logging using Loguru for better traceability.

## Technology Stack

- **Programming Language**: Python 3.11+
- **Frameworks and Libraries**:
  - **OpenAI API**: Interact with OpenAI's GPT models.
  - **Loguru**: Advanced logging capabilities.
  - **Python-dotenv**: Manage environment variables.
  - **Python-dateutil**: For date parsing.
  - **Hatch**: Environment management and packaging.
  - **Pytest**: Testing framework.
  - **Twine**: For publishing packages to PyPI.

## Installation Instructions

### Install via PyPI

**AI Assistant Manager** is available on PyPI and can be installed using `pip`:

```bash
pip install ai-assistant-manager
```

For more details, visit the [PyPI project page](https://pypi.org/project/ai-assistant-manager/).

### From Source

1. **Clone the repository**:

   ```bash
   git clone https://github.com/DEV3L/ai-assistant-manager
   cd ai-assistant-manager
   ```

2. **Set up environment variables**:

   Copy the `env.local` file to `.env` and replace placeholders with your actual OpenAI API key:

   ```bash
   cp env.local .env
   ```

   Edit `.env` to add your `OPENAI_API_KEY`:

   ```dotenv
   OPENAI_API_KEY=your_openai_api_key
   ```

3. **Set up a virtual environment**:

   **Install Hatch** (if not already installed):

   ```bash
   pip install hatch
   ```

   **Create and activate the virtual environment**:

   ```bash
   hatch env create
   hatch shell
   ```

## Usage Guide

### Environment Variables

Configure the following environment variables in your `.env` file:

- `OPENAI_API_KEY`: Your OpenAI API key.
- `OPENAI_MODEL`: The model to use (default: `gpt-4o-2024-08-06`).
- `ASSISTANT_DESCRIPTION`: Description of the assistant (default: `AI Assistant Manager`).
- `ASSISTANT_NAME`: Name of the assistant (default: `AI Assistant Manager`).
- `BIN_DIR`: Directory for binaries (default: `bin`).
- `DATA_DIR`: Directory for data files (default: `data`).
- `DATA_FILE_PREFIX`: Prefix for data files (default: `AI Assistant Manager`).

### Running the Example

To see **AI Assistant Manager** in action, you can run the provided example script:

```python
from loguru import logger

from ai_assistant_manager.assistants.assistant_service import AssistantService
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

    service.delete_assistant()

if __name__ == "__main__":
    try:
        set_env_variables()
        main()
    except Exception as e:
        logger.info(f"Error: {e}")
```

### Running the Script

```bash
python run_end_to_end.py
```

This script will:

- Export data from specified directories.
- Create an assistant service.
- Start a chat session with the assistant.
- Send a message and display the assistant's response.
- Clean up by deleting the assistant after the session.

## Available Scripts

- **Run End-to-End Test**:

  ```bash
  hatch run e2e
  ```

- **Run Unit Tests**:

  ```bash
  hatch run test
  ```

- **Publish Package to PyPI**:

  ```bash
  hatch run publish
  ```

_Note: These scripts are defined in `pyproject.toml` under `[tool.hatch.envs.default.scripts]`._

## Testing Instructions

### End-to-End Test

Run the end-to-end test to ensure the tool works as expected:

```bash
hatch run e2e
```

### Unit Tests

To run unit tests:

```bash
hatch run test
```

Coverage reports are generated using `pytest-cov`.

### Coverage Gutters

To monitor code coverage in VSCode:

1. Install the **Coverage Gutters** extension.
2. Run:

   ```bash
   Command + Shift + P => Coverage Gutters: Watch
   ```

## Project Structure Overview

```
ai-assistant-manager/
├── ai_assistant_manager/
│   ├── assistants/
│   │   └── assistant_service.py
│   ├── chats/
│   │   ├── chat.py
│   │   └── chat_response.py
│   ├── clients/
│   │   └── openai_api.py
│   ├── exporters/
│   │   ├── directory/
│   │   │   └── directory_exporter.py
│   │   ├── files/
│   │   │   └── files_exporter.py
│   │   └── exporter.py
│   ├── prompts/
│   │   ├── sample_prompt.md
│   │   └── prompt.py
│   ├── content_data.py
│   ├── env_variables.py
│   └── encoding.py
├── tests/
│   ├── assistants/
│   │   └── assistant_service_test.py
│   ├── chats/
│   │   ├── chat_test.py
│   │   └── chat_response_test.py
│   ├── clients/
│   │   └── openai_api_test.py
│   ├── exporters/
│   │   ├── directory/
│   │   │   └── directory_exporter_test.py
│   │   ├── files/
│   │   │   └── files_exporter_test.py
│   │   └── exporter_test.py
│   ├── prompts/
│   │   └── prompt_test.py
│   ├── env_variables_test.py
│   └── timer_test.py
├── .env.default
├── pyproject.toml
├── README.md
├── run_end_to_end.py
├── LICENSE
```

- **ai_assistant_manager/**: Main package containing the code.
  - **assistants/**: Assistant management services.
  - **chats/**: Chat functionalities.
  - **clients/**: OpenAI client interactions.
  - **exporters/**: Export data to files or directories.
  - **prompts/**: Manage assistant prompts.
  - **env_variables.py**: Environment variable management.
  - **encoding.py**: Encoding configurations.
- **tests/**: Contains unit tests for the code.
- **.env.default**: Template for environment variables.
- **pyproject.toml**: Project configuration and dependencies.
- **run_end_to_end.py**: Script to execute the end-to-end process.
- **LICENSE**: Project license information.

## Contributing Guidelines

We welcome contributions! Please follow these steps:

1. **Fork the repository** on GitHub.
2. **Create a new branch** for your feature or bugfix:

   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes** and commit them with clear messages.
4. **Run tests** to ensure nothing is broken:

   ```bash
   hatch run test
   ```

5. **Push to your fork** and submit a **pull request** to the `main` branch.

## Code of Conduct

By participating in this project, you agree to abide by the following guidelines:

- **Be respectful and considerate** of others.
- **Avoid discriminatory or offensive language**.
- **Report any unacceptable behavior** to the project maintainers.

## License Information

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **OpenAI** - For providing the GPT models used in assistant management.
- **Community Contributors** - Thank you to all who have contributed through issues and pull requests.

## Additional Resources

- **PyPI Project Page**: [ai-assistant-manager](https://pypi.org/project/ai-assistant-manager/)
