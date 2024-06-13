def find_matching_schema_key(schema_keys: set[str], schema_key: str) -> str | None:
    for k in schema_keys:
        if k == schema_key:
            return k
    return None
