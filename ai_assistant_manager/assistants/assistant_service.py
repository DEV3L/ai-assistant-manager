import os

from loguru import logger

from ai_assistant_manager.clients.openai_api import OpenAIClient
from ai_assistant_manager.env_variables import ENV_VARIABLES

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
        """
        Initialize the AssistantService with a client, prompt, assistant name, and data file prefix.

        :param client: The OpenAIClient instance to interact with the OpenAI API.
        :param prompt: The prompt to be used for the assistant.
        :param assistant_name: The name of the assistant (default is from environment variables).
        :param data_file_prefix: The prefix for data files (default is from environment variables).
        :param tools: The tools to be used by the assistant.
        """

        self.client = client
        self.prompt = prompt
        self.assistant_name = assistant_name if assistant_name else ENV_VARIABLES.assistant_name
        self.data_file_prefix = data_file_prefix if data_file_prefix else ENV_VARIABLES.data_file_prefix
        self.tools = tools

    def get_assistant_id(self):
        """
        Get the assistant ID, either by finding an existing one or creating a new one.

        :return: The ID of the assistant.
        """
        return self._find_existing_assistant() or self._create_assistant()

    def _find_existing_assistant(self):
        """
        Retrieve the list of assistants and find one that matches the assistant name.

        :return: The ID of the existing assistant or None if not found.
        """
        assistants = self.client.assistants_list()
        return next(
            (assistant.id for assistant in assistants if assistant.name == self.assistant_name),
            None,
        )

    def _create_assistant(self):
        """
        Create a new assistant using the client if no existing assistant is found.

        :return: The ID of the newly created assistant.
        """
        logger.info(f"Creating new assistant {self.assistant_name}")
        return self.client.assistants_create(
            self.assistant_name, self.prompt, self.get_vector_store_ids(), tools=self.tools
        ).id

    def get_vector_store_ids(self):
        """
        Get the vector store IDs, either by finding existing ones or creating new ones.

        :return: A list of vector store IDs.
        """
        return self._find_existing_vector_stores() or self.create_vector_stores()

    def _find_existing_vector_stores(self):
        """
        Retrieve the list of vector stores and find those that match the data file prefix.

        :return: A list of existing vector store IDs.
        """
        vector_stores = self.client.vector_stores_list()
        return [
            vector_store.id
            for vector_store in vector_stores
            if vector_store.name and vector_store.name.startswith(self.data_file_prefix)
        ]

    def create_vector_stores(self):
        """
        Create new vector stores if no existing vector stores are found.

        :return: A list containing the ID of the newly created vector store.
        """
        logger.info("Creating new vector stores")
        retrieval_file_ids = self.get_retrieval_file_ids()
        return [
            self._validate_vector_stores(
                self.client.vector_stores_create(f"{self.data_file_prefix} vector store", retrieval_file_ids)
            )
        ]

    def _validate_vector_stores(self, vector_store_id: str):
        """
        Validate the vector store by checking the status of its files and recreating any failed files.

        :param vector_store_id: The ID of the vector store to validate.
        :return: The validated vector store ID.
        """
        try:
            vector_store_files = self.client.vector_stores_files(vector_store_id)
            failed_files = [file.id for file in vector_store_files if file.status == "failed"]

            if not failed_files:
                return vector_store_id

            # Retrieve details of failed files
            failed_retrieval_files = [self.client.files_get(file) for file in failed_files if file]
            failed_retrieval_file_names = [self._get_file_name(file.filename) for file in failed_retrieval_files]
            failed_file_paths = [
                file_path
                for file_path in self._get_file_paths()
                if self._get_file_name(file_path) in failed_retrieval_file_names
            ]

            # Delete failed files from vector store
            [self.client.vector_stores_file_delete(vector_store_id, file_id) for file_id in failed_files]

            # Recreate failed files
            recreated_files = self._create_files(failed_file_paths)
            self.client.vector_stores_update(vector_store_id, recreated_files)

            # Recursively validate the vector store again
            return self._validate_vector_stores(vector_store_id)
        except Exception as e:
            logger.error(f"Error validating vector store {vector_store_id}: {e}")
            return self._validate_vector_stores(vector_store_id)

    def _get_file_name(self, file_path: str) -> str:
        """
        Extract the file name from the file path.

        :param file_path: The path of the file.
        :return: The name of the file.
        """
        return os.path.basename(file_path)

    def get_retrieval_file_ids(self):
        """
        Get the retrieval file IDs, either by finding existing ones or creating new ones.

        :return: A list of retrieval file IDs.
        """
        return self._find_existing_retrieval_files() or self.create_retrieval_files()

    def _find_existing_retrieval_files(self):
        """
        Retrieve the list of files and find those that match the data file prefix.

        :return: A list of existing retrieval file IDs.
        """
        files = self.client.files_list()
        return [file.id for file in files if file.filename.startswith(self.data_file_prefix)]

    def create_retrieval_files(self):
        """
        Create new retrieval files if no existing retrieval files are found.

        :return: A list of newly created retrieval file IDs.
        """
        logger.info("Creating new retrieval files")
        file_paths = self._get_file_paths()
        return self._create_files(file_paths)

    def _get_file_paths(self):
        """
        Get the paths of all files in the "bin" directory, excluding ".DS_Store" files.

        :return: A list of file paths.
        """
        return [
            os.path.join(root, file)
            for (root, _, files) in os.walk("bin")
            for file in files
            if not file.endswith(".DS_Store")
        ]

    def _create_files(self, file_paths: list[str]):
        """
        Create files using the client for each file path provided.

        :param file_paths: A list of file paths to create files from.
        :return: A list of newly created file IDs.
        """
        return [self._create_file(file_path) for file_path in file_paths]

    def _create_file(self, file_path: str):
        """
        Create a single file using the client.

        :param file_path: The path of the file to create.
        :return: The ID of the newly created file.
        """
        with open(file_path, "rb") as file:
            return self.client.files_create(file, "assistants").id

    def delete_assistant(self):
        """
        Remove the assistant and its associated vector stores and retrieval files.

        This method ensures that all resources related to the assistant are cleaned up.
        """
        logger.info(f"Removing existing {self.assistant_name} and retrieval files")

        if assistant_id := self._find_existing_assistant():
            self.client.assistants_delete(assistant_id)
        if vector_store_ids := self._find_existing_vector_stores():
            for vector_store_id in vector_store_ids:
                self.client.vector_stores_delete(vector_store_id)
        if file_ids := self._find_existing_retrieval_files():
            for file_id in file_ids:
                self.client.files_delete(file_id)
