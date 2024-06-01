import io
import json


def get_mock_uapi_json() -> str:
    with open("mock-internal.uapi.json", "r") as file:
        return file.read()
