from .tools import SAMPLE_TOOLS_PATH, get_tools


def test_get_tools():
    tools = get_tools(tools_path=SAMPLE_TOOLS_PATH)

    assert isinstance(tools, list)
    assert len(tools) > 0
