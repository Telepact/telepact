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
import math

import yaml

from .GetPathDocumentYamlCoordinatesPseudoJson import create_path_document_yaml_coordinates_pseudo_json_locator


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


def parse_telepact_yaml(text: str) -> tuple[str, callable]:
    try:
        parsed = yaml.safe_load(text)
    except yaml.YAMLError as e:
        raise ValueError(str(e)) from e

    normalized = _normalize_json_compatible_value(parsed)
    if not isinstance(normalized, list):
        raise ValueError('Telepact YAML root must be a sequence')

    return json.dumps(normalized, separators=(',', ':')), create_path_document_yaml_coordinates_pseudo_json_locator(text)
