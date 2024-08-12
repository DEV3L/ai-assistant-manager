from unittest import TestCase
from unittest.mock import MagicMock, patch

from ai_assistant_manager.clients.openai_api import OpenAIClient, build_openai_client


@patch("ai_assistant_manager.clients.openai_api.OpenAI")
def test_build_openai_client(mock_openai):
    """
    Test that build_openai_client returns an instance of OpenAI with the correct timeout.
    """
    client = build_openai_client()

    assert client is mock_openai.return_value
    mock_openai.assert_called_once_with(timeout=90)


class TestOpenAIClient(TestCase):
    client: OpenAIClient
    mock_open_ai: MagicMock

    def setUp(self):
        """
        Set up the test case with a mocked OpenAI instance.
        """
        self.mock_open_ai = MagicMock()
        self.client = OpenAIClient(self.mock_open_ai)

    def test_threads_create(self):
        """
        Test that threads_create calls the correct OpenAI API method.
        """
        self.client.threads_create()
        self.mock_open_ai.beta.threads.create.assert_called()

    def test_messages_list(self):
        """
        Test that messages_list calls the correct OpenAI API method with the correct parameters.
        """
        thread_id = "thread_id"
        self.client.messages_list(thread_id)
        self.mock_open_ai.beta.threads.messages.list.assert_called_once_with(thread_id)

    def test_messages_create(self):
        """
        Test that messages_create calls the correct OpenAI API method with the correct parameters.
        """
        thread_id = "thread_id"
        content = "Hello"
        role = "user"
        self.client.messages_create(thread_id, content, role)
        self.mock_open_ai.beta.threads.messages.create.assert_called_once_with(
            thread_id=thread_id, content=content, role=role
        )

    def test_runs_create(self):
        """
        Test that runs_create calls the correct OpenAI API method with the correct parameters.
        """
        thread_id = "thread_id"
        assistant_id = "assistant_id"
        self.client.runs_create(assistant_id, thread_id, False)
        self.mock_open_ai.beta.threads.runs.create_and_poll.assert_called_once_with(
            thread_id=thread_id, assistant_id=assistant_id, tool_choice=None
        )

    def test_runs_create_with_tool_choice(self):
        """
        Test that runs_create calls the correct OpenAI API method with tool choice.
        """
        thread_id = "thread_id"
        assistant_id = "assistant_id"
        self.client.runs_create(assistant_id, thread_id, True)
        self.mock_open_ai.beta.threads.runs.create_and_poll.assert_called_once_with(
            thread_id=thread_id, assistant_id=assistant_id, tool_choice={"type": "file_search"}
        )

    def test_runs_retrieve(self):
        """
        Test that runs_retrieve calls the correct OpenAI API method with the correct parameters.
        """
        run_id = "run_id"
        thread_id = "thread_id"
        self.client.runs_retrieve(run_id, thread_id)
        self.mock_open_ai.beta.threads.runs.retrieve.assert_called_once_with(run_id, thread_id=thread_id)

    def test_assistants_list(self):
        """
        Test that assistants_list calls the correct OpenAI API method.
        """
        self.client.assistants_list()
        self.mock_open_ai.beta.assistants.list.assert_called_once()

    def test_assistants_create(self):
        """
        Test that assistants_create calls the correct OpenAI API method with the correct parameters.
        """
        name = "assistant_name"
        instructions = "instructions"
        tools = [{"tool_name": "tool"}]
        vector_store_ids = ["vector_store_id"]
        self.client.assistants_create(name, instructions, vector_store_ids, tools)
        self.mock_open_ai.beta.assistants.create.assert_called_once_with(
            name=name,
            instructions=instructions,
            model="gpt-4o",
            tool_resources={"file_search": {"vector_store_ids": vector_store_ids}},
            tools=tools,
        )

    def test_assistants_delete(self):
        """
        Test that assistants_delete calls the correct OpenAI API method with the correct parameters.
        """
        assistant_id = "assistant_id"
        self.client.assistants_delete(assistant_id)
        self.mock_open_ai.beta.assistants.delete.assert_called_once_with(assistant_id)

    def test_files_list(self):
        """
        Test that files_list calls the correct OpenAI API method and returns the expected result.
        """
        files = self.client.files_list()
        self.mock_open_ai.files.list.assert_called_once()
        assert files == self.mock_open_ai.files.list.return_value

    def test_files_get(self):
        """
        Test that files_get calls the correct OpenAI API method with the correct parameters and returns the expected result.
        """
        file_id = "file_id"
        file = self.client.files_get(file_id)
        self.mock_open_ai.files.retrieve.assert_called_once_with(file_id)
        assert file == self.mock_open_ai.files.retrieve.return_value

    def test_files_create(self):
        """
        Test that files_create calls the correct OpenAI API method with the correct parameters.
        """
        file = MagicMock()
        purpose = "assistants"
        self.client.files_create(file, purpose)
        self.mock_open_ai.files.create.assert_called_once_with(file=file, purpose=purpose)

    def test_files_delete(self):
        """
        Test that files_delete calls the correct OpenAI API method with the correct parameters.
        """
        file_id = "file_id"
        self.client.files_delete(file_id)
        self.mock_open_ai.files.delete.assert_called_once_with(file_id)

    def test_vector_stores_list(self):
        """
        Test that vector_stores_list calls the correct OpenAI API method and returns the expected result.
        """
        vector_stores = self.client.vector_stores_list()
        self.mock_open_ai.beta.vector_stores.list.assert_called_once()
        assert vector_stores == self.mock_open_ai.beta.vector_stores.list.return_value

    def test_vector_stores_retrieve(self):
        """
        Test that vector_stores_retrieve calls the correct OpenAI API method with the correct parameters and returns the expected result.
        """
        vector_store_id = "vector_store_id"
        vector_store = self.client.vector_stores_retrieve(vector_store_id)
        self.mock_open_ai.beta.vector_stores.retrieve.assert_called_once_with(vector_store_id)
        assert vector_store == self.mock_open_ai.beta.vector_stores.retrieve.return_value

    @patch("ai_assistant_manager.clients.openai_api.time")
    def test_vector_stores_create(self, mock_time):
        """
        Test that vector_stores_create calls the correct OpenAI API method and handles polling correctly.
        """
        file_ids = ["file_id"]
        name = "vector_store_name"
        self.mock_open_ai.beta.vector_stores.retrieve.side_effect = [
            MagicMock(status="pending", file_counts=MagicMock(failed=0)),
            MagicMock(status="completed", file_counts=MagicMock(failed=0)),
        ]
        vector_store_id = self.client.vector_stores_create(name, file_ids)
        self.mock_open_ai.beta.vector_stores.create.assert_called_once_with(name=name, file_ids=file_ids)
        assert vector_store_id == self.mock_open_ai.beta.vector_stores.create.return_value.id
        assert mock_time.sleep.call_count == 1

    @patch("ai_assistant_manager.clients.openai_api.logger")
    def test_vector_stores_create_with_failed_files(self, mock_logger):
        """
        Test that vector_stores_create logs a warning if there are failed files.
        """
        file_ids = ["file_id"]
        name = "vector_store_name"
        self.mock_open_ai.beta.vector_stores.retrieve.side_effect = [
            MagicMock(status="completed", file_counts=MagicMock(failed=1)),
        ]
        self.client.vector_stores_create(name, file_ids)
        self.mock_open_ai.beta.vector_stores.create.assert_called_once_with(name=name, file_ids=file_ids)
        assert mock_logger.warning.call_count == 1

    @patch("ai_assistant_manager.clients.openai_api.time")
    @patch("ai_assistant_manager.clients.openai_api.logger")
    def test_vector_stores_update(self, mock_logger, mock_time):
        """
        Test that vector_stores_update calls the correct OpenAI API method and handles polling and logging correctly.
        """
        expected_vector_store_id = "vector_store_id"
        file_ids = ["file_id"]
        self.mock_open_ai.beta.vector_stores.retrieve.side_effect = [
            MagicMock(status="pending", file_counts=MagicMock(failed=0)),
            MagicMock(status="completed", file_counts=MagicMock(failed=1)),
        ]
        vector_store_id = self.client.vector_stores_update(expected_vector_store_id, file_ids)
        self.mock_open_ai.beta.vector_stores.files.create.assert_called_once_with(vector_store_id, file_id=file_ids[0])
        assert vector_store_id == expected_vector_store_id
        assert mock_time.sleep.call_count == 1
        assert mock_logger.warning.call_count == 1

    def test_vector_stores_delete(self):
        """
        Test that vector_stores_delete calls the correct OpenAI API method with the correct parameters.
        """
        vector_store_id = "vector_store_id"
        self.client.vector_stores_delete(vector_store_id)
        self.mock_open_ai.beta.vector_stores.delete.assert_called_once_with(vector_store_id)

    def test_vector_stores_file_delete(self):
        """
        Test that vector_stores_file_delete calls the correct OpenAI API methods with the correct parameters.
        """
        vector_store_id = "vector_store_id"
        file_id = "file_id"
        self.client.vector_stores_file_delete(vector_store_id, file_id)
        self.mock_open_ai.beta.vector_stores.files.delete.assert_called_once_with(
            file_id, vector_store_id=vector_store_id
        )
        self.mock_open_ai.files.delete.assert_called_once_with(file_id)

    def test_vector_stores_files(self):
        """
        Test that vector_stores_files calls the correct OpenAI API method with the correct parameters and returns the expected result.
        """
        vector_store_id = "vector_store_id"
        vector_store_files = self.client.vector_stores_files(vector_store_id)
        self.mock_open_ai.beta.vector_stores.files.list.assert_called_once_with(vector_store_id, limit=100)
        assert vector_store_files == self.mock_open_ai.beta.vector_stores.files.list.return_value
