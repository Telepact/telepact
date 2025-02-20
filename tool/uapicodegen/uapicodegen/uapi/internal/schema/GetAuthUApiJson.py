import os


def get_auth_uapi_json() -> str:
    file_path = os.path.join(os.path.dirname(
        __file__), "..", "..", "auth.uapi.json")
    file_path = os.path.normpath(file_path)
    with open(file_path, "r") as stream:
        return "\n".join(stream.readlines())
