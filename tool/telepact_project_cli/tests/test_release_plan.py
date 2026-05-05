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
from unittest import mock

from click.testing import CliRunner

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_ROOT))

from telepact_project_cli.cli import main
from telepact_project_cli.commands.doc_versions import _latest_released_versions
from telepact_project_cli.release_plan import (
    changed_paths_since_last_version_change,
    compute_release_manifest,
    compute_release_manifest_from_git,
)


@contextlib.contextmanager
def _pushd(path: Path):
    old_cwd = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old_cwd)


def _git(repo_root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return result.stdout.strip()


def _init_repo(repo_root: Path) -> None:
    _git(repo_root, "init")
    _git(repo_root, "config", "user.name", "Test User")
    _git(repo_root, "config", "user.email", "test@example.com")


def _write_release_targets(repo_root: Path) -> None:
    (repo_root / ".release").mkdir(exist_ok=True)
    (repo_root / ".release" / "release-targets.yaml").write_text(
        textwrap.dedent(
            """
            projects:
              py:
                paths: [lib/py]
                is_dependency_for: [cli]
              ts:
                paths: [lib/ts]
                is_dependency_for: [dart, console]
              cli:
                paths: [sdk/cli]
              console:
                paths: [sdk/console]
              dart:
                paths: [bind/dart]
              prettier:
                paths: [sdk/prettier]
                is_dependency_for: [console]
            force_all_if_changed:
              - .release/force-all.md
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )


def _commit_all(repo_root: Path, message: str) -> None:
    _git(repo_root, "add", ".")
    _git(repo_root, "commit", "-m", message)


class ReleasePlanTests(unittest.TestCase):
    def test_set_version_preserves_aligned_package_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = Path(tmp_dir)
            package_json = project_root / "package.json"
            original = '{\n  "name": "example",\n  "version": "1.2.3"\n}\n'
            package_json.write_text(original, encoding="utf-8")

            runner = CliRunner()
            with _pushd(project_root):
                result = runner.invoke(main, ["set-version", "1.2.3"])

            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertEqual(package_json.read_text(encoding="utf-8"), original)

    def test_compute_release_manifest_uses_declarative_rules_and_dependency_expansion(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            (repo_root / "VERSION.txt").write_text("1.0.0-alpha.214", encoding="utf-8")
            _write_release_targets(repo_root)

            manifest = compute_release_manifest(
                repo_root,
                changed_paths=[
                    "lib/ts/src/main.ts",
                    "sdk/prettier/package.json",
                    "README.md",
                ],
                version="1.0.0-alpha.215",
                pr_number=None,
            )

            self.assertEqual(manifest.direct_targets, ("prettier", "ts"))
            self.assertEqual(manifest.targets, ("console", "dart", "prettier", "ts"))
            self.assertEqual(
                manifest.changed_paths,
                ("README.md", "lib/ts/src/main.ts", "sdk/prettier/package.json"),
            )

    def test_changed_paths_since_last_version_change_ignores_version_bump_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            _init_repo(repo_root)
            _write_release_targets(repo_root)
            (repo_root / "VERSION.txt").write_text("1.0.0-alpha.200", encoding="utf-8")
            (repo_root / "lib" / "py").mkdir(parents=True)
            (repo_root / "lib" / "py" / "pyproject.toml").write_text(
                '[project]\nname = "telepact"\nversion = "1.0.0-alpha.200"\n',
                encoding="utf-8",
            )
            _commit_all(repo_root, "Initial release")

            (repo_root / "lib" / "py" / "impl.py").write_text("print('changed')\n", encoding="utf-8")
            _commit_all(repo_root, "Feature change")

            (repo_root / "VERSION.txt").write_text("1.0.0-alpha.201", encoding="utf-8")
            (repo_root / "lib" / "py" / "pyproject.toml").write_text(
                '[project]\nname = "telepact"\nversion = "1.0.0-alpha.201"\n',
                encoding="utf-8",
            )
            (repo_root / "doc" / "04-operate").mkdir(parents=True)
            (repo_root / "doc" / "04-operate" / "03-versions.md").write_text("# Versions\n", encoding="utf-8")
            _commit_all(repo_root, "Bump version")

            self.assertEqual(
                changed_paths_since_last_version_change(repo_root),
                ["lib/py/impl.py"],
            )

    def test_changed_paths_since_last_version_change_filters_version_file_from_git_diff(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            (repo_root / "VERSION.txt").write_text("1.0.0-alpha.214", encoding="utf-8")
            _write_release_targets(repo_root)

            with mock.patch(
                "telepact_project_cli.release_plan._version_change_commits",
                return_value=["head", "previous"],
            ), mock.patch(
                "telepact_project_cli.release_plan._resolved_commit_sha",
                return_value="not-a-version-commit",
            ), mock.patch(
                "telepact_project_cli.release_plan._git_stdout",
                side_effect=["VERSION.txt\nlib/py/impl.py\n"],
            ):
                self.assertEqual(
                    changed_paths_since_last_version_change(repo_root),
                    ["lib/py/impl.py"],
                )

    def test_compute_release_manifest_from_git_uses_previous_version_commit_as_base(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            _init_repo(repo_root)
            _write_release_targets(repo_root)
            (repo_root / "VERSION.txt").write_text("1.0.0-alpha.200", encoding="utf-8")
            (repo_root / "lib" / "py").mkdir(parents=True)
            (repo_root / "lib" / "py" / "pyproject.toml").write_text(
                '[project]\nname = "telepact"\nversion = "1.0.0-alpha.200"\n',
                encoding="utf-8",
            )
            (repo_root / "sdk" / "cli").mkdir(parents=True)
            (repo_root / "sdk" / "cli" / "pyproject.toml").write_text(
                '[project]\nname = "telepact-cli"\nversion = "1.0.0-alpha.200"\n',
                encoding="utf-8",
            )
            _commit_all(repo_root, "Initial release")

            (repo_root / "lib" / "py" / "impl.py").write_text("print('changed')\n", encoding="utf-8")
            _commit_all(repo_root, "Feature change")

            (repo_root / "VERSION.txt").write_text("1.0.0-alpha.201", encoding="utf-8")
            (repo_root / "lib" / "py" / "pyproject.toml").write_text(
                '[project]\nname = "telepact"\nversion = "1.0.0-alpha.201"\n',
                encoding="utf-8",
            )
            (repo_root / "sdk" / "cli" / "pyproject.toml").write_text(
                '[project]\nname = "telepact-cli"\nversion = "1.0.0-alpha.201"\n',
                encoding="utf-8",
            )
            _commit_all(repo_root, "Bump version")

            manifest = compute_release_manifest_from_git(repo_root)

            self.assertEqual(manifest.version, "1.0.0-alpha.201")
            self.assertEqual(manifest.direct_targets, ("py",))
            self.assertEqual(manifest.targets, ("cli", "py"))
            self.assertEqual(manifest.changed_paths, ("lib/py/impl.py",))

    def test_publish_targets_command_writes_github_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            _init_repo(repo_root)
            _write_release_targets(repo_root)
            (repo_root / "VERSION.txt").write_text("1.0.0-alpha.214", encoding="utf-8")
            (repo_root / "lib" / "py").mkdir(parents=True)
            (repo_root / "lib" / "py" / "pyproject.toml").write_text(
                '[project]\nname = "telepact"\nversion = "1.0.0-alpha.214"\n',
                encoding="utf-8",
            )
            (repo_root / "sdk" / "cli").mkdir(parents=True)
            (repo_root / "sdk" / "cli" / "pyproject.toml").write_text(
                '[project]\nname = "telepact-cli"\nversion = "1.0.0-alpha.214"\n',
                encoding="utf-8",
            )
            _commit_all(repo_root, "Initial release")

            (repo_root / "lib" / "py" / "impl.py").write_text("print('changed')\n", encoding="utf-8")
            _commit_all(repo_root, "Feature change")

            (repo_root / "VERSION.txt").write_text("1.0.0-alpha.215", encoding="utf-8")
            (repo_root / "lib" / "py" / "pyproject.toml").write_text(
                '[project]\nname = "telepact"\nversion = "1.0.0-alpha.215"\n',
                encoding="utf-8",
            )
            (repo_root / "sdk" / "cli" / "pyproject.toml").write_text(
                '[project]\nname = "telepact-cli"\nversion = "1.0.0-alpha.215"\n',
                encoding="utf-8",
            )
            _commit_all(repo_root, "Bump version")

            output_path = repo_root / "github-output.txt"
            runner = CliRunner()
            with _pushd(repo_root):
                result = runner.invoke(
                    main,
                    [
                        "publish-targets",
                        "--release-tag",
                        "1.0.0-alpha.215",
                        "--github-output",
                        str(output_path),
                    ],
                )

            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertEqual(
                output_path.read_text(encoding="utf-8").splitlines(),
                [
                    "publish_cli=true",
                    "publish_console=false",
                    "publish_go=false",
                    "publish_java=false",
                    "publish_prettier=false",
                    "publish_py=true",
                    "publish_ts=false",
                ],
            )

    def test_bump_command_updates_version_when_targets_exist(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            (repo_root / "VERSION.txt").write_text("1.0.0-alpha.214", encoding="utf-8")
            _write_release_targets(repo_root)

            runner = CliRunner()
            git_commands: list[list[str]] = []

            def subprocess_run_side_effect(args, **kwargs):
                git_commands.append(args)
                if args[:3] == ["git", "diff", "--name-only"]:
                    return subprocess.CompletedProcess(args, 0, stdout="lib/py/pyproject.toml\n")
                return subprocess.CompletedProcess(args, 0, stdout="")

            with (
                _pushd(repo_root),
                mock.patch("telepact_project_cli.commands.project_version.subprocess.run", side_effect=subprocess_run_side_effect),
                mock.patch(
                    "telepact_project_cli.commands.project_version.write_doc_versions",
                    return_value=repo_root / "doc" / "04-operate" / "03-versions.md",
                ),
            ):
                result = runner.invoke(main, ["bump"])

            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertEqual((repo_root / "VERSION.txt").read_text(encoding="utf-8"), "1.0.0-alpha.215")
            self.assertIn(
                ["git", "commit", "-m", "Bump version to 1.0.0-alpha.215\n\nRelease targets:\ncli\npy"],
                git_commands,
            )

    def test_bump_command_keeps_version_when_no_targets_exist(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            (repo_root / "VERSION.txt").write_text("1.0.0-alpha.214", encoding="utf-8")
            _write_release_targets(repo_root)

            runner = CliRunner()

            def subprocess_run_side_effect(args, **kwargs):
                if args[:3] == ["git", "diff", "--name-only"]:
                    return subprocess.CompletedProcess(args, 0, stdout="README.md\n")
                return subprocess.CompletedProcess(args, 0, stdout="")

            with (
                _pushd(repo_root),
                mock.patch("telepact_project_cli.commands.project_version.subprocess.run", side_effect=subprocess_run_side_effect),
                mock.patch(
                    "telepact_project_cli.commands.project_version.write_doc_versions",
                    return_value=repo_root / "doc" / "04-operate" / "03-versions.md",
                ) as write_doc_versions,
            ):
                result = runner.invoke(main, ["bump"])

            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertEqual((repo_root / "VERSION.txt").read_text(encoding="utf-8"), "1.0.0-alpha.214")
            write_doc_versions.assert_called_once_with(
                Path("."),
                None,
                pending_version=None,
                pending_targets=[],
            )

    def test_latest_released_versions_uses_version_change_history(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            _init_repo(repo_root)
            _write_release_targets(repo_root)

            (repo_root / "VERSION.txt").write_text("1.0.0-alpha.200", encoding="utf-8")
            (repo_root / "lib" / "py").mkdir(parents=True)
            (repo_root / "lib" / "py" / "pyproject.toml").write_text(
                '[project]\nname = "telepact"\nversion = "1.0.0-alpha.200"\n',
                encoding="utf-8",
            )
            (repo_root / "sdk" / "cli").mkdir(parents=True)
            (repo_root / "sdk" / "cli" / "pyproject.toml").write_text(
                '[project]\nname = "telepact-cli"\nversion = "1.0.0-alpha.200"\n',
                encoding="utf-8",
            )
            (repo_root / "sdk" / "prettier").mkdir(parents=True)
            (repo_root / "sdk" / "prettier" / "package.json").write_text(
                '{\n  "name": "telepact-prettier",\n  "version": "1.0.0-alpha.200"\n}\n',
                encoding="utf-8",
            )
            (repo_root / "sdk" / "console").mkdir(parents=True)
            (repo_root / "sdk" / "console" / "package.json").write_text(
                '{\n  "name": "telepact-console",\n  "version": "1.0.0-alpha.200"\n}\n',
                encoding="utf-8",
            )
            _commit_all(repo_root, "Initial release")

            (repo_root / "lib" / "py" / "impl.py").write_text("print('changed')\n", encoding="utf-8")
            _commit_all(repo_root, "Feature change one")

            (repo_root / "VERSION.txt").write_text("1.0.0-alpha.201", encoding="utf-8")
            (repo_root / "lib" / "py" / "pyproject.toml").write_text(
                '[project]\nname = "telepact"\nversion = "1.0.0-alpha.201"\n',
                encoding="utf-8",
            )
            (repo_root / "sdk" / "cli" / "pyproject.toml").write_text(
                '[project]\nname = "telepact-cli"\nversion = "1.0.0-alpha.201"\n',
                encoding="utf-8",
            )
            _commit_all(repo_root, "Bump version one")

            (repo_root / "sdk" / "prettier" / "index.js").write_text("export {};\n", encoding="utf-8")
            _commit_all(repo_root, "Feature change two")

            (repo_root / "VERSION.txt").write_text("1.0.0-alpha.202", encoding="utf-8")
            (repo_root / "sdk" / "prettier" / "package.json").write_text(
                '{\n  "name": "telepact-prettier",\n  "version": "1.0.0-alpha.202"\n}\n',
                encoding="utf-8",
            )
            (repo_root / "sdk" / "console" / "package.json").write_text(
                '{\n  "name": "telepact-console",\n  "version": "1.0.0-alpha.202"\n}\n',
                encoding="utf-8",
            )
            _commit_all(repo_root, "Bump version two")

            versions = _latest_released_versions(repo_root, ["py", "cli", "prettier", "console"])

            self.assertEqual(
                versions,
                {
                    "py": "1.0.0-alpha.201",
                    "cli": "1.0.0-alpha.201",
                    "prettier": "1.0.0-alpha.202",
                    "console": "1.0.0-alpha.202",
                },
            )


if __name__ == "__main__":
    unittest.main()
