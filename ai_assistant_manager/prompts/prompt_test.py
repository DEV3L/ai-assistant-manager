from datetime import datetime

from .prompt import SAMPLE_PROMPT_PATH, get_prompt


def test_get_prompt():
    current_date = datetime.today().date().isoformat()

    prompt = get_prompt(prompt_path=SAMPLE_PROMPT_PATH)
    assert isinstance(prompt, str)
    assert current_date in prompt
