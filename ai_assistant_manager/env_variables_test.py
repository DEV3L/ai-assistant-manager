from .env_variables import ENV_VARIABLES, set_env_variables


def test_reset_env_variables(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "OPENAI_MODEL=test_model\n"
        "ASSISTANT_DESCRIPTION=test_description\n"
        "ASSISTANT_NAME=test_name\n"
        "BIN_DIR=test_bin\n"
        "DATA_DIR=test_data\n"
        "DATA_FILE_PREFIX=test_prefix\n"
    )

    set_env_variables(str(env_file))

    assert ENV_VARIABLES.assistant_description == "test_description"
    assert ENV_VARIABLES.assistant_name == "test_name"
    assert ENV_VARIABLES.bin_dir == "test_bin"
    assert ENV_VARIABLES.data_dir == "test_data"
    assert ENV_VARIABLES.data_file_prefix == "test_prefix"
    assert ENV_VARIABLES.openai_model == "test_model"
