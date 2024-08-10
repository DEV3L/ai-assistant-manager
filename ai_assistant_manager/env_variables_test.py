from dotenv import unset_key

from ai_assistant_manager.env_variables import reset_env_variables


def test_reset_env_variables(tmp_path):
    # Create a temporary .env file
    env_file = tmp_path / ".env"
    env_file.write_text(
        "OPENAI_MODEL=test_model\n"
        "ASSISTANT_DESCRIPTION=test_description\n"
        "ASSISTANT_NAME=test_name\n"
        "BIN_DIR=test_bin\n"
        "DATA_DIR=test_data\n"
        "DATA_FILE_PREFIX=test_prefix\n"
    )

    # Call the function to reset environment variables
    reset_env_variables(str(env_file))

    from ai_assistant_manager.env_variables import (
        ASSISTANT_DESCRIPTION,
        ASSISTANT_NAME,
        BIN_DIR,
        DATA_DIR,
        DATA_FILE_PREFIX,
        OPENAI_MODEL,
    )

    # Assert the environment variables are set correctly
    assert OPENAI_MODEL == "test_model"
    assert ASSISTANT_DESCRIPTION == "test_description"
    assert ASSISTANT_NAME == "test_name"
    assert BIN_DIR == "test_bin"
    assert DATA_DIR == "test_data"
    assert DATA_FILE_PREFIX == "test_prefix"

    # Clean up environment variables
    unset_key(str(env_file), "OPENAI_MODEL")
    unset_key(str(env_file), "ASSISTANT_DESCRIPTION")
    unset_key(str(env_file), "ASSISTANT_NAME")
    unset_key(str(env_file), "BIN_DIR")
    unset_key(str(env_file), "DATA_DIR")
    unset_key(str(env_file), "DATA_FILE_PREFIX")
