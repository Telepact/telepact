import os
from pathlib import Path
from typing import Dict


def get_schema_file_map(directory: str) -> Dict[str, str]:
    final_json_documents: Dict[str, str] = {}

    try:
        paths = list(Path(directory).rglob("*.telepact.json"))
        for path in paths:
            with open(path, 'r') as file:
                content = file.read()
            relative_path = os.path.relpath(path, directory)
            final_json_documents[relative_path] = content
    except IOError as e:
        raise RuntimeError(e)

    return final_json_documents
