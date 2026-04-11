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
import subprocess
import sys
import tempfile
import textwrap
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


def _init_git_repo(repo_root: Path) -> None:
    subprocess.run(["git", "init"], cwd=repo_root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_root, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo_root, check=True)


def _write_notice(path: Path) -> None:
    path.write_text(
        textwrap.dedent(
            """
            Copyright The Telepact Authors
            Licensed under the Apache License, Version 2.0
            -------------------
            """
        ).lstrip(),
        encoding="utf-8",
    )


class LicenseHeaderTests(unittest.TestCase):
    def test_license_header_ignores_files_beneath_real_snippets_directory_marker(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            _init_git_repo(repo_root)
            _write_notice(repo_root / "NOTICE")

            ignored_file = repo_root / "site" / "src" / "snippets" / "hero" / "example.ts"
            ignored_file.parent.mkdir(parents=True)
            ignored_original = "export const ignored = true;\n"
            ignored_file.write_text(ignored_original, encoding="utf-8")

            updated_file = repo_root / "sdk" / "cli" / "example.ts"
            updated_file.parent.mkdir(parents=True)
            updated_file.write_text("export const kept = true;\n", encoding="utf-8")

            (repo_root / "site" / "src" / "snippets" / ".license-header-ignore").touch()

            subprocess.run(["git", "add", "."], cwd=repo_root, check=True)

            runner = CliRunner()
            with _pushd(repo_root):
                result = runner.invoke(main, ["license-header", "NOTICE"])

            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertEqual(ignored_file.read_text(encoding="utf-8"), ignored_original)
            self.assertNotEqual(updated_file.read_text(encoding="utf-8"), "export const kept = true;\n")
            self.assertTrue(updated_file.read_text(encoding="utf-8").startswith("//|"))
            self.assertNotIn("site/src/snippets/hero/example.ts", result.output)
            self.assertIn("sdk/cli/example.ts", result.output)

    def test_license_header_updates_files_when_no_directory_marker_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            _init_git_repo(repo_root)
            _write_notice(repo_root / "NOTICE")

            tracked_file = repo_root / "generated" / "example.ts"
            tracked_file.parent.mkdir(parents=True)
            tracked_file.write_text("export const generated = true;\n", encoding="utf-8")

            subprocess.run(["git", "add", "."], cwd=repo_root, check=True)

            runner = CliRunner()
            with _pushd(repo_root):
                result = runner.invoke(main, ["license-header", "NOTICE"])

            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertTrue(tracked_file.read_text(encoding="utf-8").startswith("//|"))


if __name__ == "__main__":
    unittest.main()
