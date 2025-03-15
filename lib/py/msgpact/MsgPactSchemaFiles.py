class MsgPactSchemaFiles():

    filenames_to_json: dict[str, str]

    def __init__(self, directory: str):
        from .internal.schema.GetSchemaFileMap import get_schema_file_map
        self.filenames_to_json = get_schema_file_map(directory)
