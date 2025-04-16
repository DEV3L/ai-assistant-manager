import io


class NamedBytesIO(io.BytesIO):
    def __init__(self, initial_bytes: bytes, name: str):
        super().__init__(initial_bytes)
        self.name = name
