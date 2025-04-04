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
    service = AssistantService(client, prompt=get_prompt())

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
