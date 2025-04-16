import os

from loguru import logger

from ai_assistant_manager.chats.chat import Chat
from ai_assistant_manager.named_bytes import NamedBytesIO

from ..clients.openai_api import OpenAIClient
from ..env_variables import ENV_VARIABLES

RETRIEVAL_TOOLS = [
    {"type": "file_search"},
]


class AssistantService:
    """
    Service class to manage AI assistants and their associated vector stores and files.
    This class interacts with the OpenAIClient to perform operations such as creating,
    finding, and deleting assistants and their related resources.
    """

    def __init__(
        self,
        client: OpenAIClient,
        *,
        prompt: str | None = None,
        assistant_name: str | None = None,
        data_file_prefix: str | None = None,
        tools: list[dict] = RETRIEVAL_TOOLS,
    ):
        self.client = client
        self.prompt = prompt
        self.assistant_name = assistant_name if assistant_name else ENV_VARIABLES.assistant_name
        self.data_file_prefix = data_file_prefix if data_file_prefix else self.assistant_name
        self.tools = tools

    def get_assistant_id(self) -> str | None:
        assistant_id = self._find_existing_assistant(self.assistant_name)
        if assistant_id:
            return assistant_id
        else:
            return self._create_assistant()

    def get_assistant_by_key(self, assistant_key: str) -> str | None:
        return self._find_existing_assistant(assistant_key)

    def build_assistant(
        self, assistant_name: str, prompt: str, vector_store_ids: list[str] = [], tools: list[dict] = RETRIEVAL_TOOLS
    ):
        logger.info(f"Creating new assistant {assistant_name}")
        return self.client.assistants_create(
            assistant_name,
            prompt,
            vector_store_ids,
            tools=tools,
        ).id

    def start_chat(self, assistant_id: str, thread_id: str | None) -> Chat:
        chat = Chat(
            self.client,
            assistant_id,
            thread_id=thread_id,
        )
        chat.start()

        return chat

    def add_file_contents_to_files(self, file_contents: NamedBytesIO):
        return self.client.files_create(file_contents, "assistants").id

    def _find_existing_assistant(self, assistant_key: str):
        assistants = self.client.assistants_list()
        return next(
            (
                assistant.id
                for assistant in assistants
                if assistant.name == assistant_key or assistant.id == assistant_key
            ),
            None,
        )

    def _create_assistant(self):
        logger.info(f"Creating new assistant {self.assistant_name}")
        return self.client.assistants_create(
            self.assistant_name,
            self.prompt,
            self.get_vector_store_ids(),
            tools=self.tools,
        ).id

    def get_vector_store_ids(self):
        return self._find_existing_vector_stores() or self.create_vector_stores()

    def _find_existing_vector_stores(self):
        vector_stores = self.client.vector_stores_list()
        return [
            vector_store.id
            for vector_store in vector_stores
            if vector_store.name and vector_store.name.startswith(self.data_file_prefix)
        ]

    def create_vector_stores(self, *, vector_store_name: str = None, file_ids: list[str] = None):
        logger.info("Creating new vector stores")

        retrieval_file_ids = file_ids or self.get_retrieval_file_ids()
        vector_store_name = vector_store_name or f"{self.data_file_prefix} vector store"

        return [self._validate_vector_stores(self.client.vector_stores_create(vector_store_name, retrieval_file_ids))]

    def _validate_vector_stores(self, vector_store_id: str):
        try:
            vector_store_files = self.client.vector_stores_files(vector_store_id)
            failed_files = [file.id for file in vector_store_files if file.status == "failed"]

            if not failed_files:
                return vector_store_id

            failed_retrieval_files = [self.client.files_get(file) for file in failed_files if file]
            failed_retrieval_file_names = [self._get_file_name(file.filename) for file in failed_retrieval_files]
            failed_file_paths = [
                file_path
                for file_path in self._get_file_paths()
                if self._get_file_name(file_path) in failed_retrieval_file_names
            ]

            [self.client.vector_stores_file_delete(vector_store_id, file_id) for file_id in failed_files]

            recreated_files = self._create_files(failed_file_paths)
            self.client.vector_stores_update(vector_store_id, recreated_files)

            return self._validate_vector_stores(vector_store_id)
        except Exception as e:
            logger.error(f"Error validating vector store {vector_store_id}: {e}")
            return self._validate_vector_stores(vector_store_id)

    def _get_file_name(self, file_path: str) -> str:
        return os.path.basename(file_path)

    def get_retrieval_file_ids(self):
        return self._find_existing_retrieval_files() or self.create_retrieval_files()

    def _find_existing_retrieval_files(self):
        files = self.client.files_list()
        return [file.id for file in files if file.filename.startswith(self.data_file_prefix)]

    def create_retrieval_files(self):
        logger.info("Creating new retrieval files")
        file_paths = self._get_file_paths()
        return self._create_files(file_paths)

    def _get_file_paths(self):
        return [
            os.path.join(root, file)
            for (root, _, files) in os.walk("bin")
            for file in files
            if not file.endswith(".DS_Store")
        ]

    def _create_files(self, file_paths: list[str]):
        return [self._create_file(file_path) for file_path in file_paths]

    def _create_file(self, file_path: str):
        with open(file_path, "rb") as file:
            return self.client.files_create(file, "assistants").id

    def delete_assistant(self):
        logger.info(f"Removing existing {self.assistant_name} and retrieval files")

        if assistant_id := self._find_existing_assistant(self.assistant_name):
            self.client.assistants_delete(assistant_id)
        if vector_store_ids := self._find_existing_vector_stores():
            for vector_store_id in vector_store_ids:
                self.client.vector_stores_delete(vector_store_id)
        if file_ids := self._find_existing_retrieval_files():
            for file_id in file_ids:
                self.client.files_delete(file_id)
