from .env_variables import ENV_VARIABLES, set_env_variables


def test_reset_env_variables(tmp_path):
    """
    Test the set_env_variables function to ensure it correctly sets environment variables
    from a .env file.

    Args:
        tmp_path: pytest fixture that provides a temporary directory unique to the test invocation.
    """
    # Create a temporary .env file with test environment variables
    env_file = tmp_path / ".env"
    env_file.write_text(
        "OPENAI_MODEL=test_model\n"
        "ASSISTANT_DESCRIPTION=test_description\n"
        "ASSISTANT_NAME=test_name\n"
        "BIN_DIR=test_bin\n"
        "DATA_DIR=test_data\n"
        "DATA_FILE_PREFIX=test_prefix\n"
    )

    # Call the function to set environment variables from the .env file
    set_env_variables(str(env_file))

    # Assert the environment variables are set correctly in the ENV_VARIABLES instance
    assert ENV_VARIABLES.assistant_description == "test_description"
    assert ENV_VARIABLES.assistant_name == "test_name"
    assert ENV_VARIABLES.bin_dir == "test_bin"
    assert ENV_VARIABLES.data_dir == "test_data"
    assert ENV_VARIABLES.data_file_prefix == "test_prefix"
    assert ENV_VARIABLES.openai_model == "test_model"
