from dataclasses import dataclass


@dataclass
class ChatResponse:
    message: str
    annotation_files: list[str]
    token_count: int


@dataclass
class MessageWithAnnotations:
    message: str
    annotation_files: list[str]


@dataclass
class Annotation:
    text: str
    file_id: str
