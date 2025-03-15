import importlib.resources as pkg_resources
from ... import json


def get_mock_vers_api_json() -> str:
    with pkg_resources.open_text(json, 'mock-internal.msgpact.json') as stream:
        return stream.read()
