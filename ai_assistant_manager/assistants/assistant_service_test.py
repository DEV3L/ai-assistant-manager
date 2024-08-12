from unittest import TestCase, mock
from unittest.mock import MagicMock, mock_open, patch

from ai_assistant_manager.assistants.assistant_service import AssistantService
from ai_assistant_manager.env_variables import ENV_VARIABLES


class TestAssistantService(TestCase):
    service: AssistantService
    prompt = "A helpful assistant"

    def setUp(self):
        """
        Set up the test case with a mocked client and an AssistantService instance.
        """
        self.mock_client = MagicMock()
        self.service = AssistantService(self.mock_client, self.prompt)

    def test_get_assistant_id_exists(self):
        """
        Test that get_assistant_id returns the correct ID when the assistant already exists.
        """
        mock_assistant = MagicMock(id="456")
        mock_assistant.name = ENV_VARIABLES.assistant_name
        self.mock_client.assistants_list = MagicMock(
            return_value=[
                mock_assistant,
            ]
        )

        result = self.service.get_assistant_id()

        assert result == "456"
        self.mock_client.assistants_list.assert_called_once()
        self.mock_client.assistants_create.assert_not_called()

    def test_get_assistant_id_not_exists(self):
        """
        Test that get_assistant_id creates a new assistant when it does not exist.
        """
        self.mock_client.assistants_list = MagicMock(return_value=[])

        result = self.service.get_assistant_id()

        assert result == self.mock_client.assistants_create.return_value.id

    def test_get_vector_store_ids_exists(self):
        """
        Test that get_vector_store_ids returns the correct IDs when vector stores already exist.
        """
        self.mock_client.vector_stores_list = MagicMock(
            return_value=[
                MagicMock(filename=f"{ENV_VARIABLES.data_file_prefix} vector store", id="654"),
            ]
        )

        result = self.service.get_vector_store_ids()

        assert result == ["654"]
        self.mock_client.vector_stores_list.assert_called_once()
        self.mock_client.create_vector_stores.assert_not_called()

    def test_create_vector_stores(self):
        """
        Test that create_vector_stores creates vector stores and returns their IDs.
        """
        expected_vector_store_id = "vector_store_id"
        expected_file_ids = ["file1_id", "file2_id"]
        self.mock_client.vector_stores_create.return_value = expected_vector_store_id
        self.mock_client.vector_stores_files.return_value = [
            MagicMock(status="completed"),
        ]

        self.service.get_retrieval_file_ids = lambda: expected_file_ids

        vector_store_ids = self.service.create_vector_stores()

        assert vector_store_ids == [expected_vector_store_id]
        self.mock_client.vector_stores_create.assert_called_with(mock.ANY, expected_file_ids)
        self.mock_client.vector_stores_files.assert_called_with(expected_vector_store_id)

    def test_create_vector_stores_with_failed_files(self):
        """
        Test that create_vector_stores handles failed files correctly.
        """
        expected_vector_store_id = "vector_store_id"
        expected_file_ids = ["file1_id", "file2_id"]
        self.mock_client.vector_stores_create.return_value = expected_vector_store_id
        self.mock_client.vector_stores_files.side_effect = [
            [MagicMock(status="failed", id="abc")],
            lambda: Exception("Failed to create vector store"),
            [MagicMock(status="completed", id="def")],
        ]
        self.mock_client.files_get.return_value = MagicMock(filename="file_name")
        self.service.get_retrieval_file_ids = lambda: expected_file_ids

        mock_os_walk = [("root", None, ["file_name"])]

        with patch("os.walk", return_value=mock_os_walk), patch("builtins.open", mock_open(read_data="data")):
            vector_store_ids = self.service.create_vector_stores()

        assert vector_store_ids == [expected_vector_store_id]
        self.mock_client.vector_stores_file_delete.assert_called_with(expected_vector_store_id, "abc")
        self.mock_client.vector_stores_create.assert_called_with(mock.ANY, expected_file_ids)
        self.mock_client.vector_stores_files.assert_called_with(expected_vector_store_id)

    def test_validate_vector_stores(self):
        """
        Test that _validate_vector_stores returns the correct vector store ID when validation is successful.
        """
        expected_vector_store_id = "vector_store_id"

        self.mock_client.vector_stores_files.return_value = [
            MagicMock(status="completed"),
        ]

        vector_store_id = self.service._validate_vector_stores(expected_vector_store_id)

        assert vector_store_id == expected_vector_store_id

    def test_get_retrieval_file_ids_exists(self):
        """
        Test that get_retrieval_file_ids returns the correct IDs when retrieval files already exist.
        """
        self.mock_client.files_list = MagicMock(
            return_value=[
                MagicMock(filename=f"{ENV_VARIABLES.data_file_prefix} blogs.json", id="456"),
            ]
        )

        result = self.service.get_retrieval_file_ids()

        assert result == ["456"]
        self.mock_client.files_list.assert_called_once()
        self.mock_client.files_create.assert_not_called()

    def test_create_retrieval_files(self):
        """
        Test that create_retrieval_files creates retrieval files and returns their IDs.
        """
        self.mock_client.files_create.return_value.id = "file_id"

        mock_os_walk = [("root", None, ["file1", "file2"])]
        expected_file_ids = ["file_id", "file_id"]

        with patch("os.walk", return_value=mock_os_walk), patch("builtins.open", mock_open(read_data="data")):
            actual_file_ids = self.service.create_retrieval_files()

        assert actual_file_ids == expected_file_ids
        self.mock_client.files_create.assert_called_with(mock.ANY, "assistants")

    # pylint: disable=protected-access
    def test_delete_assistant_with_existing_assistant_and_files(self):
        """
        Test that delete_assistant deletes the assistant and associated files when they exist.
        """
        self.service._find_existing_assistant = MagicMock(return_value="assistant_id")
        self.service._find_existing_vector_stores = MagicMock(return_value=["vs1_id", "vs2_id"])
        self.service._find_existing_retrieval_files = MagicMock(return_value=["file1_id", "file2_id"])

        self.service.delete_assistant()

        self.service._find_existing_assistant.assert_called_once()
        self.service._find_existing_vector_stores.assert_called_once()
        self.service._find_existing_retrieval_files.assert_called_once()
        self.mock_client.assistants_delete.assert_called_once_with("assistant_id")
        self.mock_client.vector_stores_delete.assert_any_call("vs1_id")
        self.mock_client.vector_stores_delete.assert_any_call("vs2_id")
        self.mock_client.files_delete.assert_any_call("file1_id")
        self.mock_client.files_delete.assert_any_call("file2_id")

    def test_delete_assistant_with_no_existing_assistant_and_files(self):
        """
        Test that delete_assistant does not delete anything when no assistant or files exist.
        """
        self.service._find_existing_assistant = MagicMock(return_value=None)
        self.service._find_existing_retrieval_files = MagicMock(return_value=None)

        self.service.delete_assistant()

        self.service._find_existing_assistant.assert_called_once()
        self.service._find_existing_retrieval_files.assert_called_once()
        self.mock_client.assistants_delete.assert_not_called()
        self.mock_client.files_delete.assert_not_called()

    # pylint: enable=protected-access
