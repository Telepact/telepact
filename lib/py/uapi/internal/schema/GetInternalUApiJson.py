import importlib.resources as pkg_resources
from ... import json


def get_internal_uapi_json() -> str:
    with pkg_resources.open_text(json, 'internal.uapi.json') as stream:
        return stream.read()
