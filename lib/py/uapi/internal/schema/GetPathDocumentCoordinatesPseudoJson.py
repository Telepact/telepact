from typing import Tuple, cast, Generator


def string_reader(s: str) -> Generator[Tuple[str, int, int], str, str]:
    row = 0
    col = 0
    for c in s:
        yield c, row, col
    return ""


def find_coordinates(path: list[object], reader: Generator[Tuple[str, int, int], str, str]) -> dict[str, object]:

    if len(path) == 0:
        return {
            'row': 0,
            'col': 0
        }

    for c, row, col in reader:
        if c == '{':
            result = find_coordinates_object(path, reader)
            if result:
                return result
        if c == '[':
            result = find_coordinates_array(path, reader)
            if result:
                return result

    raise ValueError("Path not found in document")


def find_value(reader: Generator[Tuple[str, int, int], str, str]) -> None:
    for c, row, col in reader:
        if c == '{':
            find_object(reader)
        elif c == '[':
            find_array(reader)
        elif c == '"':
            find_string(reader)
        elif c == '}':
            return
        elif c == ']':
            return
        elif c == ',':
            return


def find_object(reader: Generator[Tuple[str, int, int], str, str]) -> None:
    working_key = None
    working_string = None
    for c, row, col in reader:
        if c == '}':
            return
        elif c == '"':
            find_string(reader)
        elif c == ':':
            find_value(reader)


def find_array(reader: Generator[Tuple[str, int, int], str, str]) -> None:
    find_value(reader)

    working_index = 0
    for c, row, col in reader:
        working_index += 1
        find_value(reader)


def find_coordinates_object(path: list[object], reader: Generator[Tuple[str, int, int], str, str]) -> dict[str, object] | None:
    for c, row, col in reader:
        if c == '}':
            return None
        elif c == '"':
            working_key = find_string(reader)
        elif c == ':':
            if working_key == path[0]:
                return find_coordinates(path[1:], reader)
            else:
                find_value(reader)

    raise ValueError("Path not found in document")


def find_coordinates_array(path: list[object], reader: Generator[Tuple[str, int, int], str, str]) -> dict[str, object] | None:
    working_index = 0
    if working_index == path[0]:
        return find_coordinates(path[1:], reader)
    else:
        find_value(reader)

    for c, row, col in reader:
        working_index += 1
        if working_index == path[0]:
            return find_coordinates(path[1:], reader)
        else:
            find_value(reader)

    raise ValueError("Path not found in document")


def find_string(reader: Generator[(str, int, int), str, str]) -> str:
    working_string = ""
    for c in reader:
        if c == '"':
            return working_string
        else:
            working_string += c
    raise ValueError("String not closed")


def get_path_document_coordinates_pseudo_json(path: list[object], document: str) -> dict[str, object]:
    reader = string_reader(document)
    return find_coordinates(path, reader)
