import importlib.resources as pkg_resources
from ... import json


def get_internal_vers_api_json() -> str:
    with pkg_resources.open_text(json, 'internal.telepact.json') as stream:
        return stream.read()
