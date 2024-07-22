import time

from loguru import logger

from ai_assistant_manager.clients.openai_api import OpenAIClient
from ai_assistant_manager.timer.timer import timer

START_MESSAGE = "hello"
TOOL_CALL_PREFIX = "tc!"


class Chat:
    client: OpenAIClient
    assistant_id: str
    thread_id: str | None

    def __init__(
        self,
        client: OpenAIClient,
        assistant_id: str,
        *,
        thread_id: str | None = None,
    ):
        self.client = client
        self.assistant_id = assistant_id
        self.thread_id = thread_id

    def start(self):
        logger.info("Starting Chat")
        self.thread_id = self.thread_id or self.client.threads_create().id
        logger.info(f"Thread ID: {self.thread_id}")

    def send_user_message(self, message: str):
        self.client.messages_create(
            self.thread_id,
            self.remove_tool_call_from_message(message),
            "user",
        )
        self.run_thread(self.should_force_tool_call(message))
        return self.last_message()

    @timer("Run Thread")
    def run_thread(self, should_force_tool_call: bool):
        run = self.client.runs_create(self.assistant_id, self.thread_id, should_force_tool_call)

        self._wait_for_run_to_complete(run.id)

    def _wait_for_run_to_complete(self, run_id: str, *, step: float = 0.25, timeout_in_seconds: int = 120):
        timeout = timeout_in_seconds / step

        while timeout > 0:
            run = self.client.runs_retrieve(run_id, self.thread_id)

            if run.status in ["completed"]:
                return
            if run.status in ["failed", "expired", "cancelled", "requires_action"]:
                raise RuntimeError(f"Run failed with status: {run.status}")

            timeout -= 1
            time.sleep(step)

        raise RuntimeError(f"Run timed out after {timeout_in_seconds} seconds")

    def last_message(self) -> str:
        message_content = self._get_messages()[0].content[0]
        if hasattr(message_content, "text"):
            return message_content.text.value

        raise RuntimeError("No text content found in the messages")

    def _get_messages(self):
        return self.client.messages_list(self.thread_id).data

    def remove_tool_call_from_message(self, message):
        return message.replace(TOOL_CALL_PREFIX, "", 1) if self.should_force_tool_call(message) else message

    def should_force_tool_call(self, message):
        return message.startswith(TOOL_CALL_PREFIX)
