import time

from loguru import logger

from ..clients.openai_api import OpenAIClient
from ..timer.timer import timer
from .chat_response import ChatResponse

TOOL_CALL_PREFIX = "tc!"


class Chat:
    """
    A class to manage chat interactions with an AI assistant. This class handles the creation of threads,
    sending messages, running threads, and retrieving messages.
    """

    def __init__(
        self,
        client: OpenAIClient,
        assistant_id: str,
        *,
        thread_id: str | None = None,
    ):
        """
        Initialize the Chat instance with a client, assistant ID, and optional thread ID.

        :param client: The OpenAIClient instance to interact with the OpenAI API.
        :param assistant_id: The ID of the assistant to interact with.
        :param thread_id: The ID of the thread to use (optional).
        """
        self.client = client
        self.assistant_id = assistant_id
        self.thread_id = thread_id

    def start(self):
        """
        Start a new chat thread if one does not already exist.

        This method ensures that a thread ID is available for the chat session.
        """
        logger.info("Starting Chat")
        # Create a new thread if thread_id is not already set
        self.thread_id = self.thread_id or self.create_thread()
        logger.info(f"Thread ID: {self.thread_id}")

    def create_thread(self):
        return self.client.threads_create().id

    def send_user_message(self, message: str) -> ChatResponse:
        """
        Send a user message to the chat thread and run the thread.

        :param message: The message content to send.
        :return: The last message content from the thread.
        """
        self.client.messages_create(
            self.thread_id,
            self.remove_tool_call_from_message(message),
            "user",
        )

        # Run the thread, potentially forcing a tool call
        tokens = self.run_thread(self.should_force_tool_call(message))
        return ChatResponse(message=self.last_message(), token_count=tokens)

    @timer("Run Thread")
    def run_thread(self, should_force_tool_call: bool) -> int:
        """
        Run the thread, potentially forcing a tool call.

        :param should_force_tool_call: Whether to force a tool call during the run.
        :return: The total number of tokens used in the run.
        """
        run = self.client.runs_create(self.assistant_id, self.thread_id, should_force_tool_call)
        return self._wait_for_run_to_complete(run.id)

    def _wait_for_run_to_complete(self, run_id: str, *, step: float = 0.25, timeout_in_seconds: int = 120) -> int:
        """
        Wait for a run to complete, polling at regular intervals.

        :param run_id: The ID of the run to wait for.
        :param step: The polling interval in seconds.
        :param timeout_in_seconds: The maximum time to wait in seconds.
        :raises RuntimeError: If the run fails or times out.
        :return: The total number of tokens used in the run.
        """
        timeout = timeout_in_seconds / step

        while timeout > 0:
            run = self.client.runs_retrieve(run_id, self.thread_id)

            if run.status in ["completed"]:
                return run.usage.total_tokens
            # requires_action will need to be handled by user
            if run.status in ["failed", "expired", "cancelled", "requires_action"]:
                raise RuntimeError(f"Run failed with status: {run.status}")

            timeout -= 1
            time.sleep(step)

        raise RuntimeError(f"Run timed out after {timeout_in_seconds} seconds")

    def last_message(self) -> str:
        """
        Retrieve the last message content from the thread.

        :return: The content of the last message.
        :raises RuntimeError: If no text content is found in the messages.
        """
        message_content = self._get_messages()[0].content[0]
        if hasattr(message_content, "text"):
            return message_content.text.value

        raise RuntimeError("No text content found in the messages")

    def _get_messages(self):
        """
        Retrieve all messages from the thread.

        :return: A list of messages in the thread.
        """
        return self.client.messages_list(self.thread_id).data

    def remove_tool_call_from_message(self, message: str) -> str:
        """
        Remove the tool call prefix from the message if it exists.

        :param message: The message content to process.
        :return: The message content without the tool call prefix.
        """
        return message.replace(TOOL_CALL_PREFIX, "", 1) if self.should_force_tool_call(message) else message

    def should_force_tool_call(self, message: str) -> bool:
        """
        Determine if the message should force a tool call.

        :param message: The message content to check.
        :return: True if the message starts with the tool call prefix, False otherwise.
        """
        return message.startswith(TOOL_CALL_PREFIX)
