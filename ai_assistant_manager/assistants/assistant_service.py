import os

from loguru import logger

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
        prompt: str,
        *,
        assistant_name: str | None = None,
        data_file_prefix: str | None = None,
        tools: list[dict] = RETRIEVAL_TOOLS,
    ):
        self.client = client
        self.prompt = prompt
        self.assistant_name = assistant_name if assistant_name else ENV_VARIABLES.assistant_name
        self.data_file_prefix = data_file_prefix if data_file_prefix else ENV_VARIABLES.data_file_prefix
        self.tools = tools

    def get_assistant_id(self):
        return self._find_existing_assistant() or self._create_assistant()

    def _find_existing_assistant(self):
        assistants = self.client.assistants_list()
        return next(
            (assistant.id for assistant in assistants if assistant.name == self.assistant_name),
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

    def create_vector_stores(self):
        logger.info("Creating new vector stores")
        retrieval_file_ids = self.get_retrieval_file_ids()
        return [
            self._validate_vector_stores(
                self.client.vector_stores_create(f"{self.data_file_prefix} vector store", retrieval_file_ids)
            )
        ]

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

        if assistant_id := self._find_existing_assistant():
            self.client.assistants_delete(assistant_id)
        if vector_store_ids := self._find_existing_vector_stores():
            for vector_store_id in vector_store_ids:
                self.client.vector_stores_delete(vector_store_id)
        if file_ids := self._find_existing_retrieval_files():
            for file_id in file_ids:
                self.client.files_delete(file_id)
