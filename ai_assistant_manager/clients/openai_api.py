import time
from io import BufferedReader
from typing import Literal

from loguru import logger
from openai import OpenAI

from ..env_variables import ENV_VARIABLES
from ..timer.timer import timer


def build_openai_client():
    return OpenAI(timeout=90)


class OpenAIClient:
    def __init__(self, open_ai: OpenAI, *, open_ai_model: str | None = None):
        self.open_ai = open_ai
        self.open_ai_model = open_ai_model if open_ai_model else ENV_VARIABLES.openai_model

    @timer("OpenAIClient.threads_create")
    def threads_create(self):
        return self.open_ai.beta.threads.create()

    @timer("OpenAIClient.messages_list")
    def messages_list(self, thread_id: str):
        return self.open_ai.beta.threads.messages.list(thread_id)

    @timer("OpenAIClient.messages_create")
    def messages_create(self, thread_id: str, content: str, role: Literal["user", "assistant"]):
        return self.open_ai.beta.threads.messages.create(
            thread_id=thread_id,
            content=content,
            role=role,
        )

    @timer("OpenAIClient.runs_create")
    def runs_create(self, assistant_id: str, thread_id: str, should_force_tool_call: bool):
        return self.open_ai.beta.threads.runs.create_and_poll(
            assistant_id=assistant_id,
            thread_id=thread_id,
            tool_choice={"type": "file_search"} if should_force_tool_call else "auto",
        )

    @timer("OpenAIClient.runs_retrieve")
    def runs_retrieve(self, run_id: str, thread_id: str):
        return self.open_ai.beta.threads.runs.retrieve(run_id, thread_id=thread_id)

    @timer("OpenAIClient.runs_retrieve")
    def submit_tool_outputs_to_run(self, run_id: str, tool_call_id: str, thread_id: str, response: str):
        return self.open_ai.beta.threads.runs.submit_tool_outputs(
            run_id, thread_id=thread_id, tool_outputs=[{"output": response, "tool_call_id": tool_call_id}]
        )

    @timer("OpenAIClient.assistants_list")
    def assistants_list(self):
        return self.open_ai.beta.assistants.list()

    @timer("OpenAIClient.assistants_create")
    def assistants_create(
        self,
        name: str,
        instructions: str,
        vector_store_ids: list[str],
        tools: list[dict] = None,
    ):
        return self.open_ai.beta.assistants.create(
            name=name,
            instructions=instructions,
            model=self.open_ai_model,
            tool_resources={"file_search": {"vector_store_ids": vector_store_ids}},
            tools=tools,
        )

    @timer("OpenAIClient.assistants_delete")
    def assistants_delete(self, assistant_id: str):
        self.open_ai.beta.assistants.delete(assistant_id)

    @timer("OpenAIClient.files_list")
    def files_list(self):
        return self.open_ai.files.list()

    @timer("OpenAIClient.files_get")
    def files_get(self, file_id: str):
        return self.open_ai.files.retrieve(file_id)

    @timer("OpenAIClient.files_create")
    def files_create(self, file: BufferedReader, purpose: Literal["assistants", "batch", "fine-tune"]):
        return self.open_ai.files.create(file=file, purpose=purpose)

    @timer("OpenAIClient.files_delete")
    def files_delete(self, file_id: str):
        self.open_ai.files.delete(file_id)

    @timer("OpenAIClient.vector_stores_list")
    def vector_stores_list(self):
        return self.open_ai.vector_stores.list()

    @timer("OpenAIClient.vector_stores_retrieve")
    def vector_stores_retrieve(self, vector_store_id: str):
        return self.open_ai.vector_stores.retrieve(vector_store_id)

    @timer("OpenAIClient.vector_stores_create")
    def vector_stores_create(self, name: str, file_ids: list[str]):
        created_vector_store = self.open_ai.vector_stores.create(name=name, file_ids=file_ids)
        vector_store_id = created_vector_store.id

        while (vector_store := self.vector_stores_retrieve(vector_store_id)).status != "completed":
            logger.info("Waiting for vector store to be ready")
            time.sleep(5)

        if vector_store.file_counts.failed > 0:
            logger.warning(
                f"Some files ({vector_store.file_counts.failed}) failed when uploaded to vector store ({vector_store_id})"
            )

        return vector_store_id

    @timer("OpenAIClient.vector_stores_update")
    def vector_stores_update(self, vector_store_id: str, file_ids: list[str]):
        [self.open_ai.vector_stores.files.create(vector_store_id, file_id=file_id) for file_id in file_ids]

        while (vector_store := self.vector_stores_retrieve(vector_store_id)).status != "completed":
            logger.info("Waiting for vector store to be ready")
            time.sleep(5)

        if vector_store.file_counts.failed > 0:
            logger.warning(
                f"Some files ({vector_store.file_counts.failed}) failed when uploaded to vector store ({vector_store_id})"
            )
        return vector_store_id

    @timer("OpenAIClient.vector_stores_delete")
    def vector_stores_delete(self, vector_store_id: str):
        self.open_ai.vector_stores.delete(vector_store_id)

    @timer("OpenAIClient.vector_stores_file_delete")
    def vector_stores_file_delete(self, vector_store_id: str, file_id: str):
        self.open_ai.vector_stores.files.delete(file_id, vector_store_id=vector_store_id)
        self.files_delete(file_id)

    @timer("OpenAIClient.vector_stores_files")
    def vector_stores_files(self, vector_store_id: str):
        return self.open_ai.vector_stores.files.list(vector_store_id, limit=100)
