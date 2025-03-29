#|
#|  Copyright The Telepact Authors
#|
#|  Licensed under the Apache License, Version 2.0 (the "License");
#|  you may not use this file except in compliance with the License.
#|  You may obtain a copy of the License at
#|
#|  https://www.apache.org/licenses/LICENSE-2.0
#|
#|  Unless required by applicable law or agreed to in writing, software
#|  distributed under the License is distributed on an "AS IS" BASIS,
#|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#|  See the License for the specific language governing permissions and
#|  limitations under the License.
#|

from typing import Tuple, cast, Generator


def get_path_document_coordinates_pseudo_json(path: list[object], document: str) -> dict[str, object]:
    reader = string_reader(document)
    return find_coordinates(path, reader)


def string_reader(s: str) -> Generator[Tuple[str, int, int], str, str]:
    row = 1
    col = 0
    for c in s:
        if c == '\n':
            row += 1
            col = 0
        else:
            col += 1
        yield c, row, col
    return ""


def find_coordinates(path: list[object], reader: Generator[Tuple[str, int, int], str, str], ov_row: int | None = None, ov_col: int | None = None) -> dict[str, object]:
    #print(f"find_coordinates: path={path}")

    for c, row, col in reader:
        if len(path) == 0:
            return {
                'row': ov_row if ov_row else row,
                'col': ov_col if ov_col else col
            }

        #print(f"find_coordinates: char={c}, row={row}, col={col}")
        if c == '{':
            result = find_coordinates_object(path, reader)
            if result:
                return result
        if c == '[':
            result = find_coordinates_array(path, reader)
            if result:
                return result

    raise ValueError("Path not found in document")


def find_coordinates_object(path: list[object], reader: Generator[Tuple[str, int, int], str, str]) -> dict[str, object] | None:
    #print(f"find_coordinates_object: path={path}")
    working_key_row_start = None
    working_key_col_start = None
    for c, row, col in reader:
        #print(f"find_coordinates_object: char={c}, row={row}, col={col}")
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
    #print(f"find_coordinates_array: path={path}")
    working_index = 0
    if working_index == path[0]:
        return find_coordinates(path[1:], reader)
    else:
        find_value(reader)

    for c, row, col in reader:
        #print(f"find_coordinates_array: char={c}, row={row}, col={col}")
        working_index += 1
        #print(f"find_coordinates_array: working_index={working_index}")
        if working_index == path[0]:
            return find_coordinates(path[1:], reader)
        else:
            find_value(reader)

    raise ValueError("Path not found in document")


def find_value(reader: Generator[Tuple[str, int, int], str, str]) -> bool:
    for c, row, col in reader:
        #print(f"find_value: char={c}, row={row}, col={col}")
        if c == '{':
            find_object(reader)
            return False
        elif c == '[':
            find_array(reader)
            return False
        elif c == '"':
            find_string(reader)
            return False
        elif c == '}':
            return True
        elif c == ']':
            return True
        elif c == ',':
            return False
    raise ValueError("Value not found in document")


def find_object(reader: Generator[Tuple[str, int, int], str, str]) -> None:
    for c, row, col in reader:
        #print(f"find_object: char={c}, row={row}, col={col}")
        if c == '}':
            return
        elif c == '"':
            find_string(reader)
        elif c == ':':
            if find_value(reader):
                return


def find_array(reader: Generator[Tuple[str, int, int], str, str]) -> None:
    #print('find_array')
    if find_value(reader):
        return

    working_index = 0
    for c, row, col in reader:
        #print(f"find_array: char={c}, row={row}, col={col}")
        if c == ']':
            return
        working_index += 1
        if find_value(reader):
            return


def find_string(reader: Generator[Tuple[str, int, int], str, str]) -> str:
    working_string = ""
    for c, row, col in reader:
        #print(f"find_string: char={c}")
        if c == '"':
            return working_string
        else:
            working_string += c
    raise ValueError("String not closed")
