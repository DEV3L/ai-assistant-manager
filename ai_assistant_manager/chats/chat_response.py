from dataclasses import dataclass


@dataclass
class ChatResponse:
    message: str
    token_count: int
