#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

import json
import math
from typing import Callable

from .BuildDocumentLocatorFromYamlAst import create_document_locator_from_yaml_text


def _normalize_json_compatible_value(value: object) -> object:
    if value is None or isinstance(value, (str, bool, int)):
        return value

    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError('YAML values must be JSON-compatible')
        return value

    if isinstance(value, list):
        return [_normalize_json_compatible_value(child) for child in value]

    if isinstance(value, dict):
        normalized: dict[str, object] = {}
        for key, child in value.items():
            if not isinstance(key, str):
                raise ValueError('YAML values must be JSON-compatible')
            normalized[key] = _normalize_json_compatible_value(child)
        return normalized

    raise ValueError('YAML values must be JSON-compatible')


def parse_telepact_yaml(text: str) -> tuple[str, Callable[[list[object]], dict[str, object]] | None]:
    import yaml

    try:
        parsed = yaml.safe_load(text)
    except yaml.YAMLError as e:
        raise ValueError(str(e)) from e

    normalized = _normalize_json_compatible_value(parsed)
    if not isinstance(normalized, list):
        raise ValueError('Telepact YAML root must be a sequence')

    return json.dumps(normalized, separators=(',', ':')), create_document_locator_from_yaml_text(text)
