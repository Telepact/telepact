import importlib.resources as importlib_resources


def get_auth_uapi_json() -> str:
    with importlib_resources.open_text("uapi", "auth.uapi.json") as stream:
        return "\n".join(stream.readlines())
