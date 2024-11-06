import json

SAMPLE_TOOLS_PATH = "ai_assistant_manager/tools/tools.json"


def get_tools(*, tools_path: str = SAMPLE_TOOLS_PATH):
    with open(tools_path, "r") as file:
        return json.load(file)
