from loguru import logger

from ai_assistant_manager.assistants.assistant_service import (
    AssistantService,
)
from ai_assistant_manager.chats.chat import Chat
from ai_assistant_manager.clients.openai_api import OpenAIClient, build_openai_client
from ai_assistant_manager.exporters.files.files_exporter import FilesExporter


def main():
    FilesExporter("about.txt").export()

    assistant_name = "AI-Assistant-Manager-Test"
    logger.info(f"Building {assistant_name}")

    client = OpenAIClient(build_openai_client())
    service = AssistantService(client, "You are a helpful assistant")

    logger.info("Removing existing assistant and category files")
    service.delete_assistant()

    assistant_id = service.get_assistant_id()
    logger.info(f"Assistant ID: {assistant_id}")

    chat = Chat(client, assistant_id)
    chat.start()

    message = "What is the AI Assistant Manager?"
    print(f"\nMessage:\n{message}")

    start_response = chat.send_user_message(message)
    print(f"\n{service.assistant_name}:\n{start_response}")

    service.delete_assistant()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.info(f"Error: {e}")
