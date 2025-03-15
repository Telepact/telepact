import importlib.resources as pkg_resources
from ... import json


def get_auth_vers_api_json() -> str:
    with pkg_resources.open_text(json, 'auth.msgpact.json') as stream:
        return stream.read()
