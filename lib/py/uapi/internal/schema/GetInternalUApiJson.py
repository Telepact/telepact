import json
import os


def get_internal_uapi_json() -> str:
    with open(os.path.join(os.path.dirname(__file__), "internal.uapi.json"), "r") as file:
        return file.read()
