# AI Assistant Manager

This repository provides tools and services to manage OpenAI Assistants, including creating, listing, and deleting assistants, as well as handling vector stores and retrieval files. It includes end-to-end and unit tests, and leverages the Hatch build system for environment management and testing.

## Setup

1. Clone the repository:

```bash
git clone https://github.com/DEV3L/open-ai-assistant
cd open-ai-assistant
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

## Testing

### End to End Test

```bash
hatch run end-to-end
```

### Unit Tests

```bash
hatch run test
```

Coverage Gutters:

```bash
Command + Shift + P => Coverage Gutters: Watch
```
