from typing import Tuple, cast, Generator


def string_reader(s: str) -> Generator[Tuple[str, int, int], str, str]:
    row = 0
    col = 0
    for c in s:
        print(f"string_reader: char={c}, row={row}, col={col}")
        if c == '\n':
            row += 1
            col = 0
        else:
            col += 1
        yield c, row, col
    return ""


def find_coordinates(path: list[object], reader: Generator[Tuple[str, int, int], str, str], ov_row: int | None = None, ov_col: int | None = None) -> dict[str, object]:
    print(f"find_coordinates: path={path}")

    for c, row, col in reader:
        if len(path) == 0:
            return {
                'row': ov_row if ov_row else row,
                'col': ov_col if ov_col else col
            }

        print(f"find_coordinates: char={c}, row={row}, col={col}")
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
        print(f"find_value: char={c}, row={row}, col={col}")
        if c == '{':
            return find_object(reader)
        elif c == '[':
            return find_array(reader)
        elif c == '"':
            find_string(reader)
            return
        elif c == '}':
            return
        elif c == ']':
            return
        elif c == ',':
            return


def find_object(reader: Generator[Tuple[str, int, int], str, str]) -> None:
    for c, row, col in reader:
        print(f"find_object: char={c}, row={row}, col={col}")
        if c == '}':
            return
        elif c == '"':
            find_string(reader)
        elif c == ':':
            find_value(reader)


def find_array(reader: Generator[Tuple[str, int, int], str, str]) -> None:
    for c, row, col in reader:
        print(f"find_array: char={c}, row={row}, col={col}")
        find_value(reader)

    working_index = 0
    for c, row, col in reader:
        working_index += 1
        find_value(reader)


def find_coordinates_object(path: list[object], reader: Generator[Tuple[str, int, int], str, str]) -> dict[str, object] | None:
    print(f"find_coordinates_object: path={path}")
    working_key_row_start = None
    working_key_col_start = None
    for c, row, col in reader:
        print(f"find_coordinates_object: char={c}, row={row}, col={col}")
        if c == '}':
            return None
        elif c == '"':
            working_key_row_start = row
            working_key_col_start = col
            working_key = find_string(reader)
        elif c == ':':
            if working_key == path[0]:
                return find_coordinates(path[1:], reader, working_key_row_start, working_key_col_start)
            else:
                find_value(reader)

    raise ValueError("Path not found in document")


def find_coordinates_array(path: list[object], reader: Generator[Tuple[str, int, int], str, str]) -> dict[str, object] | None:
    print(f"find_coordinates_array: path={path}")
    working_index = 0
    if working_index == path[0]:
        return find_coordinates(path[1:], reader)
    else:
        find_value(reader)

    for c, row, col in reader:
        print(f"find_coordinates_array: char={c}, row={row}, col={col}")
        working_index += 1
        print(f"find_coordinates_array: working_index={working_index}")
        if working_index == path[0]:
            return find_coordinates(path[1:], reader)
        else:
            find_value(reader)

    raise ValueError("Path not found in document")


def find_string(reader: Generator[Tuple[str, int, int], str, str]) -> str:
    working_string = ""
    for c, row, col in reader:
        print(f"find_string: char={c}")
        if c == '"':
            return working_string
        else:
            working_string += c
    raise ValueError("String not closed")


def get_path_document_coordinates_pseudo_json(path: list[object], document: str) -> dict[str, object]:
    print(
        f"get_path_document_coordinates_pseudo_json: path={path}, document={document}")
    reader = string_reader(document)
    return find_coordinates(path, reader)
