import importlib.resources as importlib_resources


def get_internal_uapi_json() -> str:
    with importlib_resources.open_text("uapi", "internal.uapi.json") as stream:
        return "\n".join(stream.readlines())
