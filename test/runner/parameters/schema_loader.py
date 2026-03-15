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
from pathlib import Path
import subprocess


def load_schema_definitions(path: Path) -> list[dict[str, object]]:
    if path.suffix == '.yaml':
        loaded = json.loads(
            subprocess.run(
                [
                    'ruby',
                    '-e',
                    'require "json"; require "yaml"; print JSON.generate(YAML.safe_load(File.read(ARGV[0]), permitted_classes: [], permitted_symbols: [], aliases: false))',
                    str(path),
                ],
                check=True,
                capture_output=True,
                text=True,
            ).stdout
        )
    else:
        loaded = json.loads(path.read_text())

    if not isinstance(loaded, list):
        raise AssertionError(f'Expected schema file {path} to contain a top-level list')

    return loaded


def normalize_schema_docstrings(value):
    if isinstance(value, list):
        return [normalize_schema_docstrings(item) for item in value]

    if isinstance(value, dict):
        normalized = {}
        for key, inner_value in value.items():
            if key == '///' and isinstance(inner_value, (list, str)):
                if isinstance(inner_value, list):
                    normalized_lines = [item.strip() if item.strip() != '' else '' for item in inner_value]
                    normalized[key] = '\n'.join(normalized_lines)
                else:
                    normalized[key] = inner_value.strip()
            else:
                normalized[key] = normalize_schema_docstrings(inner_value)
        return normalized

    return value
