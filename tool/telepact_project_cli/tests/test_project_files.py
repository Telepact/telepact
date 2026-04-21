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

from telepact_project_cli.project_files import find_local_project_file, read_project_version, write_project_version


class ProjectFilesTests(unittest.TestCase):
    def test_find_local_project_file_respects_priority_order(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = Path(tmp_dir)
            (project_root / "package.json").write_text('{"version":"1.2.3"}\n', encoding="utf-8")
            (project_root / "pyproject.toml").write_text('[project]\nversion = "2.0.0"\n', encoding="utf-8")

            self.assertEqual(find_local_project_file(project_root), project_root / "package.json")

    def test_write_project_version_updates_pyproject_project_table(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = Path(tmp_dir)
            pyproject = project_root / "pyproject.toml"
            pyproject.write_text('[project]\nname = "example"\nversion = "1.2.3"\n', encoding="utf-8")

            write_project_version(pyproject, "1.2.4")

            self.assertEqual(read_project_version(pyproject), "1.2.4")


if __name__ == "__main__":
    unittest.main()
