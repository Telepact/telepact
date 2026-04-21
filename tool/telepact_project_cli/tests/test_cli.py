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

import contextlib
import os
import sys
import tempfile
import unittest
from pathlib import Path

from click.testing import CliRunner

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_ROOT))

from telepact_project_cli.cli import main


@contextlib.contextmanager
def _pushd(path: Path):
    old_cwd = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old_cwd)


class CliTests(unittest.TestCase):
    def test_gitignore_add_and_remove_preserve_newlines(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            gitignore = repo_root / ".gitignore"
            gitignore.write_text("first\n", encoding="utf-8")

            runner = CliRunner()
            with _pushd(repo_root):
                add_result = runner.invoke(main, ["gitignore", "--add", "second"])
                remove_result = runner.invoke(main, ["gitignore", "--remove", "first"])

            self.assertEqual(add_result.exit_code, 0, msg=add_result.output)
            self.assertEqual(remove_result.exit_code, 0, msg=remove_result.output)
            self.assertEqual(gitignore.read_text(encoding="utf-8"), "second\n")


if __name__ == "__main__":
    unittest.main()
