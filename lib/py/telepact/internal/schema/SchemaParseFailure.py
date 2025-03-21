class SchemaParseFailure:
    def __init__(self, document_name: str, path: list[object], reason: str, data: dict[str, object]) -> None:
        self.document_name = document_name
        self.path = path
        self.reason = reason
        self.data = data
