class SchemaParseFailure:
    def __init__(self, path: list[object], reason: str, data: dict[str, object], key: str | None) -> None:
        self.path = path
        self.reason = reason
        self.data = data
        self.key = key
