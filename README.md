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

- `OPENAI_MODEL`: The model to use (default: `gpt-4o`)
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
