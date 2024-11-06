import json
import time
from dataclasses import dataclass

from loguru import logger

from ..clients.openai_api import OpenAIClient
from ..timer.timer import timer
from .chat_response import ChatResponse

TOOL_CALL_PREFIX = "tc!"


class Chat:
    def __init__(self, client: OpenAIClient, assistant_id: str, *, thread_id: str | None = None):
        self.client = client
        self.assistant_id = assistant_id
        self.thread_id = thread_id

    def start(self):
        logger.info("Starting Chat")
        self.thread_id = self.thread_id or self.create_thread()
        logger.info(f"Thread ID: {self.thread_id}")

    def create_thread(self):
        return self.client.threads_create().id

    def send_user_message(self, message: str) -> ChatResponse:
        self.client.messages_create(
            self.thread_id,
            self.remove_tool_call_from_message(message),
            "user",
        )
        tokens = self.run_thread(self.should_force_tool_call(message))
        return ChatResponse(message=self.last_message(), token_count=tokens)

    @timer("Submit Tool Outputs")
    def submit_tool_outputs(self, run_id: str, tool_call_id: str, response: str) -> int:
        self.client.submit_tool_outputs_to_run(run_id, tool_call_id, self.thread_id, response)
        tokens = self._wait_for_run_to_complete(run_id)
        return ChatResponse(message=self.last_message(), token_count=tokens)

    @timer("Run Thread")
    def run_thread(self, should_force_tool_call: bool = False) -> int:
        run = self.client.runs_create(self.assistant_id, self.thread_id, should_force_tool_call)
        return self._wait_for_run_to_complete(run.id)

    def _wait_for_run_to_complete(self, run_id: str, *, step: float = 0.25, timeout_in_seconds: int = 120) -> int:
        timeout = timeout_in_seconds / step

        while timeout > 0:
            run = self.client.runs_retrieve(run_id, self.thread_id)

            if run.status in ["completed"]:
                return run.usage.total_tokens
            if run.status in ["requires_action"] and run.required_action.type == "submit_tool_outputs":
                tool_call = run.required_action.submit_tool_outputs.tool_calls[0]
                tool_call_id = tool_call.id
                name = tool_call.function.name
                arguments = tool_call.function.arguments
                raise RequiresActionException(
                    f"Run requires action with status: {run.status}",
                    data=ActionData(
                        run_id=run_id, tool_call_id=tool_call_id, name=name, arguments=json.loads(arguments)
                    ),
                )
            if run.status in ["failed", "expired", "cancelled"]:
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

    def remove_tool_call_from_message(self, message: str) -> str:
        return message.replace(TOOL_CALL_PREFIX, "", 1) if self.should_force_tool_call(message) else message

    def should_force_tool_call(self, message: str) -> bool:
        return message.startswith(TOOL_CALL_PREFIX)


@dataclass
class ActionData:
    run_id: str
    tool_call_id: str
    name: str
    arguments: dict


class RequiresActionException(Exception):
    def __init__(self, message: str, *, data: ActionData):
        super().__init__(message)
        self.data = data
