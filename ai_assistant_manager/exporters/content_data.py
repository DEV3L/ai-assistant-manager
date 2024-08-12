from dataclasses import dataclass


@dataclass(kw_only=True)
class ContentData:
    id: str
    title: str
    body: str
    date: str
