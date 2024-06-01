from typing import Any, List, Dict


def get_type(value: Any) -> str:
    if value is None:
        return "Null"
    elif isinstance(value, bool):
        return "Boolean"
    elif isinstance(value, (int, float)):
        return "Number"
    elif isinstance(value, str):
        return "String"
    elif isinstance(value, list):
        return "Array"
    elif isinstance(value, dict):
        return "Object"
    else:
        return "Unknown"
