from loguru import logger

from src.assistants.assistant_service import (
    AssistantService,
)
from src.clients.openai_api import OpenAIClient, build_openai_client


def main():
    assistant_name = "AI-Assistant-Manager-Test"

    logger.info(f"Building {assistant_name}")

    client = OpenAIClient(build_openai_client())
    service = AssistantService(client, "You are a helpful assistant", "test", assistant_name)

    logger.info("Removing existing assistant and category files")
    service.delete_assistant()

    assistant_id = service.get_assistant_id()

    logger.info(f"Assistant ID: {assistant_id}")

    service.delete_assistant()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.info(f"Error: {e}")
