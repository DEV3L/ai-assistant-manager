import time
from io import BufferedReader
from typing import Literal

from loguru import logger
from openai import OpenAI

from ai_assistant_manager.env_variables import OPENAI_MODEL
from ai_assistant_manager.timer.timer import timer


def build_openai_client():
    """
    Build and return an OpenAI client with a specified timeout.

    :return: An instance of OpenAI client with a 90-second timeout.
    """
    return OpenAI(timeout=90)


class OpenAIClient:
    """
    A client class to interact with the OpenAI API, providing various methods to manage threads,
    messages, runs, assistants, files, and vector stores.
    """

    def __init__(self, open_ai: OpenAI, *, open_ai_model: str = OPENAI_MODEL):
        """
        Initialize the OpenAIClient with an OpenAI instance.

        :param open_ai: An instance of the OpenAI client.
        """
        self.open_ai = open_ai
        self.open_ai_model = open_ai_model

    @timer("OpenAIClient.threads_create")
    def threads_create(self):
        """
        Create a new thread using the OpenAI API.

        :return: The created thread object.
        """
        return self.open_ai.beta.threads.create()

    @timer("OpenAIClient.messages_list")
    def messages_list(self, thread_id: str):
        """
        List all messages in a specified thread.

        :param thread_id: The ID of the thread to list messages from.
        :return: A list of messages in the thread.
        """
        return self.open_ai.beta.threads.messages.list(thread_id)

    @timer("OpenAIClient.messages_create")
    def messages_create(self, thread_id: str, content: str, role: Literal["user", "assistant"]):
        """
        Create a new message in a specified thread.

        :param thread_id: The ID of the thread to create a message in.
        :param content: The content of the message.
        :param role: The role of the message sender (either "user" or "assistant").
        :return: The created message object.
        """
        return self.open_ai.beta.threads.messages.create(
            thread_id=thread_id,
            content=content,
            role=role,
        )

    @timer("OpenAIClient.runs_create")
    def runs_create(self, assistant_id: str, thread_id: str, should_force_tool_call: bool):
        """
        Create and poll a new run in a specified thread.

        :param assistant_id: The ID of the assistant to create a run for.
        :param thread_id: The ID of the thread to create a run in.
        :param should_force_tool_call: Whether to force a tool call during the run.
        :return: The created run object.
        """
        return self.open_ai.beta.threads.runs.create_and_poll(
            assistant_id=assistant_id,
            thread_id=thread_id,
            tool_choice={"type": "file_search"} if should_force_tool_call else None,
        )

    @timer("OpenAIClient.runs_retrieve")
    def runs_retrieve(self, run_id: str, thread_id: str):
        """
        Retrieve a specific run in a specified thread.

        :param run_id: The ID of the run to retrieve.
        :param thread_id: The ID of the thread the run belongs to.
        :return: The retrieved run object.
        """
        return self.open_ai.beta.threads.runs.retrieve(run_id, thread_id=thread_id)

    @timer("OpenAIClient.assistants_list")
    def assistants_list(self):
        """
        List all assistants.

        :return: A list of assistants.
        """
        return self.open_ai.beta.assistants.list()

    @timer("OpenAIClient.assistants_create")
    def assistants_create(
        self,
        name: str,
        instructions: str,
        vector_store_ids: list[str],
        tools: list[dict] = None,
    ):
        """
        Create a new assistant with specified parameters.

        :param name: The name of the assistant.
        :param instructions: The instructions for the assistant.
        :param vector_store_ids: A list of vector store IDs associated with the assistant.
        :param tools: A list of tools to be used by the assistant (optional).
        :return: The created assistant object.
        """
        return self.open_ai.beta.assistants.create(
            name=name,
            instructions=instructions,
            model=self.open_ai_model,
            tool_resources={"file_search": {"vector_store_ids": vector_store_ids}},
            tools=tools,
        )

    @timer("OpenAIClient.assistants_delete")
    def assistants_delete(self, assistant_id: str):
        """
        Delete a specified assistant.

        :param assistant_id: The ID of the assistant to delete.
        """
        self.open_ai.beta.assistants.delete(assistant_id)

    @timer("OpenAIClient.files_list")
    def files_list(self):
        """
        List all files.

        :return: A list of files.
        """
        return self.open_ai.files.list()

    @timer("OpenAIClient.files_get")
    def files_get(self, file_id: str):
        """
        Retrieve a specific file.

        :param file_id: The ID of the file to retrieve.
        :return: The retrieved file object.
        """
        return self.open_ai.files.retrieve(file_id)

    @timer("OpenAIClient.files_create")
    def files_create(self, file: BufferedReader, purpose: Literal["assistants", "batch", "fine-tune"]):
        """
        Create a new file with a specified purpose.

        :param file: The file to be uploaded.
        :param purpose: The purpose of the file (e.g., "assistants", "batch", "fine-tune").
        :return: The created file object.
        """
        return self.open_ai.files.create(file=file, purpose=purpose)

    @timer("OpenAIClient.files_delete")
    def files_delete(self, file_id: str):
        """
        Delete a specified file.

        :param file_id: The ID of the file to delete.
        """
        self.open_ai.files.delete(file_id)

    @timer("OpenAIClient.vector_stores_list")
    def vector_stores_list(self):
        """
        List all vector stores.

        :return: A list of vector stores.
        """
        return self.open_ai.beta.vector_stores.list()

    @timer("OpenAIClient.vector_stores_retrieve")
    def vector_stores_retrieve(self, vector_store_id: str):
        """
        Retrieve a specific vector store.

        :param vector_store_id: The ID of the vector store to retrieve.
        :return: The retrieved vector store object.
        """
        return self.open_ai.beta.vector_stores.retrieve(vector_store_id)

    @timer("OpenAIClient.vector_stores_create")
    def vector_stores_create(self, name: str, file_ids: list[str]):
        """
        Create a new vector store with specified parameters.

        :param name: The name of the vector store.
        :param file_ids: A list of file IDs to be included in the vector store.
        :return: The ID of the created vector store.
        """
        created_vector_store = self.open_ai.beta.vector_stores.create(name=name, file_ids=file_ids)
        vector_store_id = created_vector_store.id

        # Poll the vector store until its status is "completed"
        while (vector_store := self.vector_stores_retrieve(vector_store_id)).status != "completed":
            logger.info("Waiting for vector store to be ready")
            time.sleep(5)

        # Log a warning if any files failed to upload to the vector store
        if vector_store.file_counts.failed > 0:
            logger.warning(
                f"Some files ({vector_store.file_counts.failed}) failed when uploaded to vector store ({vector_store_id})"
            )

        return vector_store_id

    @timer("OpenAIClient.vector_stores_update")
    def vector_stores_update(self, vector_store_id: str, file_ids: list[str]):
        """
        Update a vector store by adding new files to it.

        :param vector_store_id: The ID of the vector store to update.
        :param file_ids: A list of file IDs to add to the vector store.
        :return: The ID of the updated vector store.
        """
        # Add each file to the vector store
        [self.open_ai.beta.vector_stores.files.create(vector_store_id, file_id=file_id) for file_id in file_ids]

        # Poll the vector store until its status is "completed"
        while (vector_store := self.vector_stores_retrieve(vector_store_id)).status != "completed":
            logger.info("Waiting for vector store to be ready")
            time.sleep(5)

        # Log a warning if any files failed to upload to the vector store
        if vector_store.file_counts.failed > 0:
            logger.warning(
                f"Some files ({vector_store.file_counts.failed}) failed when uploaded to vector store ({vector_store_id})"
            )
        return vector_store_id

    @timer("OpenAIClient.vector_stores_delete")
    def vector_stores_delete(self, vector_store_id: str):
        """
        Delete a specified vector store.

        :param vector_store_id: The ID of the vector store to delete.
        """
        self.open_ai.beta.vector_stores.delete(vector_store_id)

    @timer("OpenAIClient.vector_stores_file_delete")
    def vector_stores_file_delete(self, vector_store_id: str, file_id: str):
        """
        Delete a specific file from a vector store and also delete the file itself.

        :param vector_store_id: The ID of the vector store.
        :param file_id: The ID of the file to delete.
        """
        self.open_ai.beta.vector_stores.files.delete(file_id, vector_store_id=vector_store_id)
        self.files_delete(file_id)

    @timer("OpenAIClient.vector_stores_files")
    def vector_stores_files(self, vector_store_id: str):
        """
        List all files in a specified vector store.

        :param vector_store_id: The ID of the vector store to list files from.
        :return: A list of files in the vector store.
        """
        return self.open_ai.beta.vector_stores.files.list(vector_store_id, limit=100)
