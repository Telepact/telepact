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
