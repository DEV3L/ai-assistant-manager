from unittest import TestCase
from unittest.mock import MagicMock, patch

import pytest
from openai.types.beta.threads.text import Text
from openai.types.beta.threads.text_content_block import TextContentBlock

from src.chats.chat import Chat


class TestChat(TestCase):
    chat: Chat
    assistant_id = "assistant_id"

    mock_client: MagicMock

    def setUp(self):
        self.mock_client = MagicMock()
        self.chat = Chat(self.mock_client, self.assistant_id)

    def test_chat_start_sets_thread_id(self):
        self.mock_client.threads_create.return_value.id = "thread_id"

        self.chat.start()

        assert self.chat.thread_id == "thread_id"

    def test_chat_start_with_thread(self):
        self.chat.thread_id = "my_thread_id"

        self.chat.start()

        assert self.chat.thread_id == "my_thread_id"

    def test_send_user_message(self):
        self.mock_client.messages_create.return_value = None
        self.mock_client.messages_list.return_value.data = [{"content": "Hello"}]
        self.chat.thread_id = "thread_id"
        self.chat.run_thread = MagicMock()
        self.chat.last_message = MagicMock(return_value="Hello")

        result = self.chat.send_user_message("Test message")

        assert result == "Hello"
        self.mock_client.messages_create.assert_called_once_with("thread_id", "Test message", "user")
        self.chat.run_thread.assert_called_once()
        self.chat.last_message.assert_called_once()

    def test_chat_run_thread(self):
        self.mock_client.runs_create.return_value.id = "run_id"
        self.chat.thread_id = "thread_id"

        with patch.object(self.chat, "_wait_for_run_to_complete") as mock_wait_for_run_to_complete:
            self.chat.run_thread(False)

        mock_wait_for_run_to_complete.assert_called_once_with("run_id")

    def test_wait_for_run_to_complete_success(self):
        self.mock_client.runs_retrieve.return_value.status = "completed"

        with patch("time.sleep", return_value=None):
            # pylint: disable=protected-access
            self.chat._wait_for_run_to_complete("run_id")

        self.mock_client.runs_retrieve.assert_called_with(
            "run_id",
            self.chat.thread_id,
        )

    def test_wait_for_run_to_complete_failure(self):
        self.mock_client.runs_retrieve.return_value.status = "failed"

        with patch("time.sleep", return_value=None):
            with pytest.raises(RuntimeError, match="Run failed with status: failed"):
                # pylint: disable=protected-access
                self.chat._wait_for_run_to_complete("run_id")

        self.mock_client.runs_retrieve.assert_called_with(
            "run_id",
            self.chat.thread_id,
        )

    def test_wait_for_run_to_complete_timeout(self):
        self.mock_client.runs_retrieve.return_value.status = "running"

        with patch("time.sleep", return_value=None):
            with pytest.raises(RuntimeError, match="Run timed out after 1 seconds"):
                # pylint: disable=protected-access
                self.chat._wait_for_run_to_complete("run_id", timeout_in_seconds=1)

        self.mock_client.runs_retrieve.assert_called_with(
            "run_id",
            self.chat.thread_id,
        )

    def test_last_message(self):
        self.mock_client.messages_list.return_value.data = [
            MagicMock(content=[MagicMock(text=MagicMock(value="Hello"))])
        ]
        self.chat.thread_id = "thread_id"

        result = self.chat.last_message()

        assert result == "Hello"
        self.mock_client.messages_list.assert_called_once_with("thread_id")

    def test_last_message_with_text_content(self):
        self.chat._get_messages = MagicMock(
            return_value=[
                MagicMock(content=[TextContentBlock(text=Text(annotations=[], value="Hello, world!"), type="text")])
            ]
        )
        assert self.chat.last_message() == "Hello, world!"

    def test_last_message_with_no_text_content(self):
        not_text = MagicMock()
        delattr(not_text, "text")
        self.chat._get_messages = MagicMock(return_value=[MagicMock(content=[not_text])])
        with pytest.raises(RuntimeError, match="No text content found in the messages"):
            self.chat.last_message()

    def test_remove_tool_call_from_message(self):
        assert self.chat.remove_tool_call_from_message("tc! call") == " call"
        assert self.chat.remove_tool_call_from_message(" tc! call") == " tc! call"

    def test_should_force_tool_call(self):
        assert self.chat.should_force_tool_call("tc!")
        assert not self.chat.should_force_tool_call(" tc!")
