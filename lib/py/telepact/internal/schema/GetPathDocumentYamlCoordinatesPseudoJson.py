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

import json
import re


def _serialize_path(path: list[object]) -> str:
    return json.dumps(path)


def _normalize_document(text: str) -> str:
    return text.replace('\r\n', '\n').replace('\r', '\n')


def _trim_comment(text: str) -> str:
    quote: str | None = None
    for index, char in enumerate(text):
        if char in ('"', "'"):
            quote = None if quote == char else (char if quote is None else quote)
            continue
        if quote is None and char == '#':
            return text[:index].rstrip()
    return text.rstrip()


def _count_indent(line: str) -> int:
    indent = 0
    while indent < len(line) and line[indent] == ' ':
        indent += 1
    return indent


def _get_line_info(lines: list[str], index: int) -> dict[str, object]:
    content = _trim_comment(lines[index])
    return {'index': index, 'indent': _count_indent(lines[index]), 'content': content, 'trimmed': content.strip()}


def _peek_significant_line(lines: list[str], start_index: int) -> dict[str, object] | None:
    for index in range(start_index, len(lines)):
        info = _get_line_info(lines, index)
        if info['trimmed'] != '':
            return info
    return None


def _reject_unsupported_yaml(line: str) -> None:
    trimmed = _trim_comment(line).strip()
    if trimmed == '':
        return
    if trimmed in ('---', '...'):
        raise ValueError('YAML multi-document markers are not supported')
    if re.search(r'^\s*[&*]', line) or re.search(r':\s*[&*]', line) or re.search(r'-\s*[&*]', line):
        raise ValueError('YAML anchors and aliases are not supported')
    if re.search(r'^\s*!', line) or re.search(r':\s*!', line) or re.search(r'-\s*!', line):
        raise ValueError('YAML tags are not supported')
    if '<<:' in trimmed:
        raise ValueError('YAML merge keys are not supported')
def _decode_quoted_string(text: str) -> str:
    if text.startswith('"'):
        return json.loads(text)

    result = ''
    index = 1
    while index < len(text) - 1:
        if text[index] == "'" and index + 1 < len(text) - 1 and text[index + 1] == "'":
            result += "'"
            index += 2
            continue
        result += text[index]
        index += 1
    return result


def _parse_scalar(text: str) -> object:
    if text == 'null':
        return None
    if text == 'true':
        return True
    if text == 'false':
        return False
    if re.match(r'^-?(0|[1-9][0-9]*)$', text):
        return int(text)
    if re.match(r'^-?(0|[1-9][0-9]*)\.[0-9]+$', text):
        return float(text)
    if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
        return _decode_quoted_string(text)
    return text


def _parse_key_token(text: str) -> str:
    trimmed = text.strip()
    if (trimmed.startswith('"') and trimmed.endswith('"')) or (trimmed.startswith("'") and trimmed.endswith("'")):
        return _decode_quoted_string(trimmed)
    if trimmed in ('///', '->'):
        return trimmed
    if not re.match(r'^[A-Za-z][A-Za-z0-9_.!]*$', trimmed):
        raise ValueError('Invalid YAML key')
    return trimmed


def _find_mapping_colon(text: str) -> int:
    quote: str | None = None
    for index, char in enumerate(text):
        if char in ('"', "'"):
            quote = None if quote == char else (char if quote is None else quote)
            continue
        if quote is None and char == ':' and (index + 1 == len(text) or text[index + 1] == ' '):
            return index
    return -1


def _parse_inline_entry(text: str, base_column: int) -> dict[str, object]:
    leading_spaces = len(text) - len(text.lstrip())
    trimmed = text.lstrip()
    colon_index = _find_mapping_colon(trimmed)
    if colon_index < 0:
        raise ValueError('Expected YAML mapping entry')
    key_text = trimmed[:colon_index].rstrip()
    remainder = trimmed[colon_index + 1:]
    value_text = remainder.lstrip()
    spaces_before_value = len(remainder) - len(value_text)
    return {
        'key': _parse_key_token(key_text),
        'key_column': base_column + leading_spaces,
        'value_text': value_text,
        'value_column': base_column + leading_spaces + colon_index + 1 + spaces_before_value,
    }


def _starts_flow_collection(text: str) -> bool:
    return text.startswith('{') or text.startswith('[')


def _skip_flow_whitespace(text: str, index: int) -> int:
    current = index
    while current < len(text) and text[current] == ' ':
        current += 1
    return current


def _find_flow_delimiter(text: str, start_index: int, delimiter: str) -> int:
    quote: str | None = None
    for index in range(start_index, len(text)):
        char = text[index]
        if char in ('"', "'"):
            quote = None if quote == char else (char if quote is None else quote)
            continue
        if quote is None and char == delimiter:
            return index
    return -1


def _find_flow_scalar_end(text: str, start_index: int) -> int:
    quote: str | None = None
    for index in range(start_index, len(text)):
        char = text[index]
        if char in ('"', "'"):
            quote = None if quote == char else (char if quote is None else quote)
            continue
        if quote is None and char in (',', ']', '}'):
            return index
    return len(text)


def _parse_flow_node(text: str, start_index: int, row: int, base_column: int, path: list[object], locations: dict[str, dict[str, object]]) -> dict[str, object]:
    index = _skip_flow_whitespace(text, start_index)
    if index >= len(text):
        raise ValueError('Unexpected end of YAML flow collection')

    if text[index] == '[':
        value: list[object] = []
        current = _skip_flow_whitespace(text, index + 1)
        if current < len(text) and text[current] == ']':
            return {'value': value, 'next_index': current + 1}

        while current < len(text):
            item_path = list(path) + [len(value)]
            locations[_serialize_path(item_path)] = {'row': row, 'col': base_column + current}
            parsed = _parse_flow_node(text, current, row, base_column, item_path, locations)
            value.append(parsed['value'])
            current = _skip_flow_whitespace(text, int(parsed['next_index']))
            if current < len(text) and text[current] == ',':
                current = _skip_flow_whitespace(text, current + 1)
                continue
            if current < len(text) and text[current] == ']':
                return {'value': value, 'next_index': current + 1}
            break

        raise ValueError('Invalid YAML flow collection')

    if text[index] == '{':
        value: dict[str, object] = {}
        current = _skip_flow_whitespace(text, index + 1)
        if current < len(text) and text[current] == '}':
            return {'value': value, 'next_index': current + 1}

        while current < len(text):
            key_start = current
            colon_index = _find_flow_delimiter(text, key_start, ':')
            if colon_index < 0:
                raise ValueError('Expected YAML mapping entry')
            key_text = text[key_start:colon_index].rstrip()
            key = _parse_key_token(key_text)
            key_path = list(path) + [key]
            serialized_path = _serialize_path(key_path)
            if serialized_path in locations or key in value:
                raise ValueError('Duplicate YAML key')
            locations[serialized_path] = {'row': row, 'col': base_column + key_start}

            current = _skip_flow_whitespace(text, colon_index + 1)
            parsed = _parse_flow_node(text, current, row, base_column, key_path, locations)
            value[key] = parsed['value']
            current = _skip_flow_whitespace(text, int(parsed['next_index']))
            if current < len(text) and text[current] == ',':
                current = _skip_flow_whitespace(text, current + 1)
                continue
            if current < len(text) and text[current] == '}':
                return {'value': value, 'next_index': current + 1}
            break

        raise ValueError('Invalid YAML flow collection')

    end_index = _find_flow_scalar_end(text, index)
    return {'value': _parse_scalar(text[index:end_index].strip()), 'next_index': end_index}


def _parse_block_scalar(lines: list[str], start_index: int, parent_indent: int, folded: bool) -> dict[str, object]:
    index = start_index
    block_lines: list[str] = []
    min_indent: int | None = None

    while index < len(lines):
        info = _get_line_info(lines, index)
        if info['trimmed'] != '' and info['indent'] <= parent_indent:
            break
        if info['trimmed'] != '':
            min_indent = info['indent'] if min_indent is None else min(min_indent, info['indent'])
        block_lines.append(lines[index])
        index += 1

    content_indent = min_indent if min_indent is not None else parent_indent + 1
    normalized_lines = []
    for line in block_lines:
        if _trim_comment(line).strip() == '':
            normalized_lines.append('')
        else:
            normalized_lines.append(line[min(content_indent, len(line)):])

    if not folded:
        return {'value': '\n'.join(normalized_lines), 'next_index': index}

    value = ''
    for line in normalized_lines:
        if line == '':
            value += '\n'
        else:
            if value != '' and not value.endswith('\n'):
                value += ' '
            value += line
    return {'value': value, 'next_index': index}


def _parse_value_text(lines: list[str], info: dict[str, object], current_indent: int, path: list[object], value_text: str, value_column: int, locations: dict[str, dict[str, object]]) -> dict[str, object]:
    if value_text == '{}':
        return {'value': {}, 'next_index': info['index'] + 1}
    if value_text == '[]':
        return {'value': [], 'next_index': info['index'] + 1}
    if value_text == '|':
        return _parse_block_scalar(lines, info['index'] + 1, current_indent, False)
    if value_text == '>':
        return _parse_block_scalar(lines, info['index'] + 1, current_indent, True)
    if value_text == '':
        next_info = _peek_significant_line(lines, info['index'] + 1)
        if next_info is None or next_info['indent'] <= current_indent:
            return {'value': None, 'next_index': info['index'] + 1}
        return _parse_node(lines, next_info['index'], next_info['indent'], path, locations)
    if _starts_flow_collection(value_text):
        parsed = _parse_flow_node(value_text, 0, int(info['index']) + 1, value_column, path, locations)
        if _skip_flow_whitespace(value_text, int(parsed['next_index'])) != len(value_text):
            raise ValueError('Invalid YAML flow collection')
        return {'value': parsed['value'], 'next_index': info['index'] + 1}
    return {'value': _parse_scalar(value_text), 'next_index': info['index'] + 1}


def _parse_map_entries(lines: list[str], start_index: int, indent: int, path: list[object], locations: dict[str, dict[str, object]], initial_entry: dict[str, object] | None = None) -> dict[str, object]:
    value: dict[str, object] = {}
    line_index = start_index
    first_entry = initial_entry

    while True:
        info = first_entry['info'] if first_entry is not None else _peek_significant_line(lines, line_index)
        if info is None:
            break
        if first_entry is None and info['indent'] < indent:
            break
        if first_entry is None and (info['indent'] != indent or str(info['trimmed']).startswith('-')):
            if first_entry is not None:
                raise ValueError('Unexpected YAML mapping indentation')
            break

        entry_text = first_entry['text'] if first_entry is not None else str(info['content'])[indent:]
        base_column = int(first_entry['base_column']) if first_entry is not None else indent + 1
        entry = _parse_inline_entry(str(entry_text), base_column)
        key_path = list(path) + [entry['key']]
        serialized_path = _serialize_path(key_path)
        if serialized_path in locations or entry['key'] in value:
            raise ValueError('Duplicate YAML key')
        locations[serialized_path] = {'row': info['index'] + 1, 'col': entry['key_column']}

        parsed_value = _parse_value_text(lines, info, indent, key_path, str(entry['value_text']), int(entry['value_column']), locations)
        value[str(entry['key'])] = parsed_value['value']
        line_index = int(parsed_value['next_index'])
        first_entry = None

    return {'value': value, 'next_index': line_index}


def _parse_sequence(lines: list[str], start_index: int, indent: int, path: list[object], locations: dict[str, dict[str, object]]) -> dict[str, object]:
    value: list[object] = []
    line_index = start_index

    while True:
        info = _peek_significant_line(lines, line_index)
        if info is None:
            break
        if info['indent'] < indent:
            break
        trimmed = str(info['trimmed'])
        if info['indent'] != indent or not (trimmed == '-' or trimmed.startswith('- ')):
            break

        item_path = list(path) + [len(value)]
        locations[_serialize_path(item_path)] = {'row': info['index'] + 1, 'col': indent + 1}

        after_dash = str(info['content'])[indent + 1:]
        value_text = after_dash.lstrip()
        if value_text == '':
            next_info = _peek_significant_line(lines, info['index'] + 1)
            if next_info is None or next_info['indent'] <= indent:
                value.append(None)
                line_index = info['index'] + 1
                continue
            parsed_node = _parse_node(lines, next_info['index'], next_info['indent'], item_path, locations)
            value.append(parsed_node['value'])
            line_index = int(parsed_node['next_index'])
            continue

        value_column = indent + 2 + (len(after_dash) - len(value_text))
        if not _starts_flow_collection(value_text) and _find_mapping_colon(value_text) >= 0:
            parsed_node = _parse_map_entries(lines, info['index'] + 1, indent + 2, item_path, locations, {
                'info': info,
                'text': after_dash,
                'base_column': indent + 2,
            })
            value.append(parsed_node['value'])
            line_index = int(parsed_node['next_index'])
            continue

        parsed_value = _parse_value_text(lines, info, indent, item_path, value_text, value_column, locations)
        value.append(parsed_value['value'])
        line_index = int(parsed_value['next_index'])

    return {'value': value, 'next_index': line_index}


def _parse_node(lines: list[str], start_index: int, indent: int, path: list[object], locations: dict[str, dict[str, object]]) -> dict[str, object]:
    info = _peek_significant_line(lines, start_index)
    if info is None:
        raise ValueError('Unexpected end of YAML document')
    if info['indent'] != indent:
        raise ValueError('Unexpected YAML indentation')
    trimmed = str(info['trimmed'])
    if trimmed == '-' or trimmed.startswith('- '):
        return _parse_sequence(lines, start_index, indent, path, locations)
    return _parse_map_entries(lines, start_index, indent, path, locations)


def create_path_document_yaml_coordinates_pseudo_json_locator(text: str) -> callable:
    normalized = _normalize_document(text)
    lines = normalized.split('\n')
    for line in lines:
        if re.match(r'^ *\t', line):
            raise ValueError('Tabs are not supported in Telepact YAML')
        _reject_unsupported_yaml(line)

    first_info = _peek_significant_line(lines, 0)
    if first_info is None or first_info['indent'] != 0:
        raise ValueError('Telepact YAML must start at the root sequence')

    locations: dict[str, dict[str, object]] = {}
    parsed = _parse_node(lines, first_info['index'], 0, [], locations)
    if not isinstance(parsed['value'], list):
        raise ValueError('Telepact YAML root must be a sequence')

    def locator(path: list[object]) -> dict[str, object]:
        return locations.get(_serialize_path(path), {'row': 1, 'col': 1})

    return locator


def get_path_document_yaml_coordinates_pseudo_json(path: list[object], document: str) -> dict[str, object]:
    return create_path_document_yaml_coordinates_pseudo_json_locator(document)(path)
