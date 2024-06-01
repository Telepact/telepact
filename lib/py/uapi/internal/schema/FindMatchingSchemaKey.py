from typing import Set, Optional


def find_matching_schema_key(schema_keys: Set[str], schema_key: str) -> Optional[str]:
    for k in schema_keys:
        if k == schema_key:
            return k
    return None
