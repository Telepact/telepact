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

import sys
import tempfile
import unittest
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_ROOT))

from telepact_project_cli.project_files import (
    find_supported_project_file,
    iter_supported_project_files,
    read_version,
    write_version,
)


class ProjectFilesTests(unittest.TestCase):
    def test_find_supported_project_file_uses_expected_priority(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = Path(tmp_dir)
            (project_root / "package.json").write_text('{"version":"1.2.3"}', encoding="utf-8")
            (project_root / "pyproject.toml").write_text('[project]\nversion = "4.5.6"\n', encoding="utf-8")

            self.assertEqual(find_supported_project_file(project_root), project_root / "package.json")
            self.assertEqual(iter_supported_project_files(project_root), [
                project_root / "package.json",
                project_root / "pyproject.toml",
            ])

    def test_write_version_round_trips_supported_formats(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = Path(tmp_dir)
            package_json = project_root / "package.json"
            pyproject = project_root / "pyproject.toml"
            pubspec = project_root / "pubspec.yaml"

            package_json.write_text('{\n  "name": "example",\n  "version": "1.2.3"\n}\n', encoding="utf-8")
            pyproject.write_text('[project]\nname = "example"\nversion = "1.2.3"\n', encoding="utf-8")
            pubspec.write_text('name: example\nversion: 1.2.3\n', encoding="utf-8")

            for path in [package_json, pyproject, pubspec]:
                write_version(path, "2.0.0")
                self.assertEqual(read_version(path), "2.0.0")

            self.assertEqual(
                package_json.read_text(encoding="utf-8"),
                '{\n  "name": "example",\n  "version": "2.0.0"\n}\n',
            )


if __name__ == "__main__":
    unittest.main()
