from dataclasses import dataclass


@dataclass
class ChatResponse:
    """
    Represents a response in a chat.

    Attributes:
        message (str): The message content of the chat response.
        token_count (int): The total token count in the chat response.
    """

    message: str
    token_count: int
