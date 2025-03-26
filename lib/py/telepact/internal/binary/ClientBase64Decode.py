from typing import cast
import base64


def client_base64_decode(message: list[object]) -> None:
    headers = cast(dict[str, object], message[0])
    body = cast(dict[str, object], message[1])
    
    base64_paths = cast(dict[str, object], headers['@base64'])

    base64_decode(body, base64_paths)


def base64_decode(given: object, base64_paths: dict[str, object]) -> None:
    if isinstance(given, dict):
        for key, value in given.items():
            this_base64_path = base64_paths.get(key)
            if not this_base64_path:
                continue

            if this_base64_path is True:
                new_value = base64.b64decode(value)
                given[key] = new_value
            else:
                base64_decode(value, cast(dict[str, object], this_base64_path))
    elif isinstance(given, list):
        for item in given:
            base64_decode(item, base64_paths)
