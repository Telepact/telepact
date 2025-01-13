from typing import Tuple, cast


def get_path_document_coordinates_pseudo_json(path: list[object], document: str) -> dict[str, object]:

    working_document = document
    working_path = path.copy()

    stack = [('', 0, 0)]

    row = 0
    col = 0

    def get_pseudo_json(last: Tuple[str, int, int]) -> dict[str, object]:
        return {
            "row": last[1],
            "col": last[2]
        }

    print(f"Working path: {working_path}")

    working_s = ""
    last_s = ""
    last = ('', 0, 0)
    working_index = 0

    while working_document:
        c = working_document[0]
        working_document = working_document[1:]
        print(f"Processing character: {c}")

        col += 1
        print(f"Updated col: {col}")

        if c == '\n':
            row += 1
            col = 0
            print(f"Newline found. Updated row: {row}, reset col: {col}")

        if c == '{':
            print(f"Found '{{' at row {row}, col {col}")
            stack.append(('{', row, col))
            print(f"Updated stack: {stack}")
        elif c == '"' and stack[-1][0] != '"':
            print(f"Found '\"' at row {row}, col {col}")
            stack.append(('"', row, col))
            print(f"Updated stack: {stack}")
        elif c != '"' and stack[-1][0] == '"':
            print(f"Appending to working_s: {c}")
            working_s += c
            print(f"Updated working_s: {working_s}")
        elif c == '"' and stack[-1][0] == '"':
            print(f"Closing '\"' at row {row}, col {col}")
            last_s = working_s
            working_s = ""
            last = stack.pop()
            print(
                f"Updated last_s: {last_s}, reset working_s, updated stack: {stack}")
        elif c == ':':
            print(f"Found ':' at row {row}, col {col}")
            if last_s == working_path[0]:
                print(f"Matched path segment: {last_s}")
                working_path = working_path[1:]
                print(f"Updated working_path: {working_path}")
                if not working_path:
                    print("Path fully matched")
                    return get_pseudo_json(last)
            stack.append((':', row, col))
            print(f"Updated stack: {stack}")
        elif c == ',' and stack[-1][0] == ':':
            print(f"Found ',' after ':' at row {row}, col {col}")
            last = stack.pop()
            print(f"Updated stack: {stack}")
        elif c == '}' and stack[-1][0] == ':':
            print(f"Found '}}' after ':' at row {row}, col {col}")
            last = stack.pop()
            print(f"Updated stack: {stack}")
            last = stack.pop()
            print(f"Updated stack: {stack}")
        elif c == '}':
            print(f"Found '}}' at row {row}, col {col}")
            last = stack.pop()
            print(f"Updated stack: {stack}")
        elif c == '[':
            print(f"Found '[' at row {row}, col {col}")
            stack.append(('[', row, col))
            print(f"Updated stack: {stack}")
        elif c == ',' and stack[-1][0] == '[':
            print(f"Found ',' in array at row {row}, col {col}")
            working_index += 1
            print(f"Updated working_index: {working_index}")
            if working_index == working_path[0]:
                print(f"Matched array index: {working_index}")
                working_path = working_path[1:]
                print(f"Updated working_path: {working_path}")
                if not working_path:
                    print("Path fully matched")
                    return get_pseudo_json(last)
        elif c == ']':
            print(f"Found ']' at row {row}, col {col}")
            last = stack.pop()
            print(f"Updated stack: {stack}")

    raise ValueError("Path not found in document")
