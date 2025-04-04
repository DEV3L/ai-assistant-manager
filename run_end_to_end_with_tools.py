from loguru import logger

from ai_assistant_manager.assistants.assistant_service import (
    RETRIEVAL_TOOLS,
    AssistantService,
)
from ai_assistant_manager.chats.chat import Chat, RequiresActionException
from ai_assistant_manager.clients.openai_api import OpenAIClient, build_openai_client
from ai_assistant_manager.env_variables import ENV_VARIABLES, set_env_variables
from ai_assistant_manager.exporters.directory.directory_exporter import DirectoryExporter
from ai_assistant_manager.exporters.files.files_exporter import FilesExporter
from ai_assistant_manager.prompts.prompt import SAMPLE_PROMPT_PATH_WITH_TOOLS, get_prompt
from ai_assistant_manager.tools.tools import get_tools
from ai_assistant_manager.tools.weather import get_weather

assistant_name = "AI-Assistant-Manager-Tool-Test"


def main():
    DirectoryExporter("directory").export()
    FilesExporter("about.txt").export()

    logger.info(f"Building {assistant_name}")

    tools_from_file = get_tools()
    tools_from_file.extend(RETRIEVAL_TOOLS)

    client = OpenAIClient(build_openai_client())
    service = AssistantService(
        client, prompt=get_prompt(prompt_path=SAMPLE_PROMPT_PATH_WITH_TOOLS), tools=tools_from_file
    )

    logger.info("Removing existing assistant and category files")
    service.delete_assistant()

    assistant_id = service.get_assistant_id()
    logger.info(f"Assistant ID: {assistant_id}")

    chat = Chat(client, assistant_id)
    chat.start()

    message = "What is the weather like today?"
    print(f"\nMessage:\n{message}")

    try:
        chat_response = chat.send_user_message(message)
        assert False
    except RequiresActionException as e:
        print(f"\n{service.assistant_name}:\nTOOL_CALL: {e.data}")
        weather_result = get_weather(e.data.arguments["location"])
        print(weather_result)

        chat_response = chat.submit_tool_outputs(e.data.run_id, e.data.tool_call_id, weather_result)
        print(f"\n{service.assistant_name}:\n{chat_response.message}")
        print(f"\nTokens: {chat_response.token_count}")

    service.delete_assistant()


if __name__ == "__main__":
    try:
        set_env_variables()
        ENV_VARIABLES.assistant_name = assistant_name
        main()
    except Exception as e:
        logger.info(f"Error: {e}")
