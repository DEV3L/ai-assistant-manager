from datetime import datetime

from ai_assistant_manager.encoding import UTF_8

SAMPLE_PROMPT_PATH = "ai_assistant_manager/prompts/sample_prompt.md"

CURRENT_DATE_VARIABLE = "{{CURRENT_DATE}}"


def get_prompt(*, prompt_path: str = SAMPLE_PROMPT_PATH):
    with open(prompt_path, "r", encoding=UTF_8) as prompt:
        current_date = datetime.today().date().isoformat()
        return prompt.read().replace(CURRENT_DATE_VARIABLE, current_date)
