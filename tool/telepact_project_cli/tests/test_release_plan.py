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
import json
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_ROOT))

from telepact_project_cli.cli import main
from telepact_project_cli.commands.doc_versions import _latest_released_versions
from telepact_project_cli.release_plan import (
    changed_paths_for_commits,
    compute_release_manifest,
    load_release_manifest,
    release_commits_since_last_bump,
    write_release_manifest,
)


@contextlib.contextmanager
def _pushd(path: Path):
    old_cwd = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old_cwd)


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
            (repo_root / ".release").mkdir()
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
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )

            manifest = compute_release_manifest(
                repo_root,
                changed_paths=[
                    "lib/ts/src/main.ts",
                    "sdk/prettier/package.json",
                    "README.md",
                ],
                version="1.0.0-alpha.215",
                pr_number=300,
            )
            manifest_path = write_release_manifest(repo_root, manifest)
            loaded = load_release_manifest(repo_root)

            self.assertEqual(manifest.direct_targets, ("prettier", "ts"))
            self.assertEqual(loaded["targets"], ["console", "dart", "prettier", "ts"])
            self.assertEqual(loaded["changed_paths"], [
                "README.md",
                "lib/ts/src/main.ts",
                "sdk/prettier/package.json",
            ])
            self.assertEqual(loaded["included_commits"], [])
            self.assertEqual(manifest_path.resolve(), (repo_root / ".release" / "release-manifest.json").resolve())

    def test_compute_release_manifest_marks_all_targets_when_force_all_file_changes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            (repo_root / "VERSION.txt").write_text("1.0.0-alpha.214", encoding="utf-8")
            (repo_root / ".release").mkdir()
            (repo_root / ".release" / "release-targets.yaml").write_text(
                textwrap.dedent(
                    """
                    projects:
                      java:
                        paths: [lib/java]
                      py:
                        paths: [lib/py]
                        is_dependency_for: [cli]
                      ts:
                        paths: [lib/ts]
                        is_dependency_for: [dart, console]
                      go:
                        paths: [lib/go]
                      dart:
                        paths: [bind/dart]
                      cli:
                        paths: [sdk/cli]
                      console:
                        paths: [sdk/console]
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

            manifest = compute_release_manifest(
                repo_root,
                changed_paths=[".release/force-all.md"],
                version="1.0.0-alpha.215",
                pr_number=301,
            )

            self.assertEqual(
                manifest.direct_targets,
                ("cli", "console", "dart", "go", "java", "prettier", "py", "ts"),
            )
            self.assertEqual(manifest.targets, manifest.direct_targets)

    def test_publish_targets_command_writes_github_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            (repo_root / "VERSION.txt").write_text("1.0.0-alpha.214", encoding="utf-8")
            (repo_root / ".release").mkdir()
            (repo_root / ".release" / "release-manifest.json").write_text(
                json.dumps(
                    {
                        "version": "1.0.0-alpha.214",
                        "pr_number": 7,
                        "changed_paths": ["lib/py/pyproject.toml"],
                        "direct_targets": ["py"],
                        "included_commits": [],
                        "targets": ["cli", "py"],
                    },
                    indent=2,
                    sort_keys=True,
                ) + "\n",
                encoding="utf-8",
            )

            output_path = repo_root / "github-output.txt"
            runner = CliRunner()
            with _pushd(repo_root):
                result = runner.invoke(
                    main,
                    [
                        "publish-targets",
                        "--release-tag",
                        "1.0.0-alpha.214",
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

    def test_create_pull_request_uses_github_sdk(self) -> None:
        runner = CliRunner()
        fake_pull_request = MagicMock(number=123, html_url="https://example.test/pr/123")
        fake_repo = MagicMock()
        fake_repo.create_pull.return_value = fake_pull_request
        fake_github = MagicMock()
        fake_github.get_repo.return_value = fake_repo

        with patch("telepact_project_cli.cli.Github", return_value=fake_github) as github_class:
            result = runner.invoke(
                main,
                [
                    "create-pull-request",
                    "--title",
                    "Bump version to 1.0.0-alpha.999",
                    "--body",
                    "Release targets:\npy",
                    "--head",
                    "bump-version",
                    "--base",
                    "main",
                    "--no-draft",
                    "--no-maintainer-can-modify",
                ],
                env={
                    "GITHUB_TOKEN": "test-token",
                    "GITHUB_REPOSITORY": "Telepact/telepact",
                },
            )

        self.assertEqual(result.exit_code, 0, msg=result.output)
        github_class.assert_called_once_with("test-token")
        fake_github.get_repo.assert_called_once_with("Telepact/telepact")
        fake_repo.create_pull.assert_called_once_with(
            title="Bump version to 1.0.0-alpha.999",
            body="Release targets:\npy",
            head="bump-version",
            base="main",
            draft=False,
            maintainer_can_modify=False,
        )
        self.assertIn("Created pull request #123", result.output)

    def test_latest_released_versions_prefers_manifest_history_and_falls_back_to_legacy_commits(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            subprocess.run(["git", "init"], cwd=repo_root, check=True, capture_output=True, text=True)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_root, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo_root, check=True)

            (repo_root / "VERSION.txt").write_text("1.0.0-alpha.200", encoding="utf-8")
            subprocess.run(["git", "add", "VERSION.txt"], cwd=repo_root, check=True)
            subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_root, check=True)

            subprocess.run(
                [
                    "git",
                    "commit",
                    "--allow-empty",
                    "-m",
                    "Bump version to 1.0.0-alpha.201 (#1)\n\nRelease targets:\njava",
                ],
                cwd=repo_root,
                check=True,
            )

            (repo_root / ".release").mkdir()
            (repo_root / ".release" / "release-manifest.json").write_text(
                json.dumps(
                    {
                        "version": "1.0.0-alpha.202",
                        "pr_number": 2,
                        "changed_paths": ["lib/py/pyproject.toml"],
                        "direct_targets": ["py"],
                        "included_commits": [],
                        "targets": ["cli", "py"],
                    },
                    indent=2,
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )
            subprocess.run(["git", "add", ".release/release-manifest.json"], cwd=repo_root, check=True)
            subprocess.run(
                ["git", "commit", "-m", "Bump version to 1.0.0-alpha.202 (#2)"],
                cwd=repo_root,
                check=True,
            )

            versions = _latest_released_versions(repo_root, ["java", "py", "cli"])

            self.assertEqual(
                versions,
                {
                    "py": "1.0.0-alpha.202",
                    "cli": "1.0.0-alpha.202",
                    "java": "1.0.0-alpha.201",
                },
            )

    def test_release_commits_since_last_bump_collects_linear_history_since_previous_bump(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            subprocess.run(["git", "init"], cwd=repo_root, check=True, capture_output=True, text=True)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_root, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo_root, check=True)

            (repo_root / "VERSION.txt").write_text("1.0.0-alpha.200", encoding="utf-8")
            subprocess.run(["git", "add", "VERSION.txt"], cwd=repo_root, check=True)
            subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_root, check=True)

            subprocess.run(
                ["git", "commit", "--allow-empty", "-m", "Bump version to 1.0.0-alpha.201"],
                cwd=repo_root,
                check=True,
            )

            py_file = repo_root / "lib" / "py" / "client.py"
            py_file.parent.mkdir(parents=True)
            py_file.write_text("print('py')\n", encoding="utf-8")
            subprocess.run(["git", "add", "lib/py/client.py"], cwd=repo_root, check=True)
            subprocess.run(["git", "commit", "-m", "Add Python client (#10)"], cwd=repo_root, check=True)

            prettier_file = repo_root / "sdk" / "prettier" / "index.js"
            prettier_file.parent.mkdir(parents=True)
            prettier_file.write_text("export {};\n", encoding="utf-8")
            subprocess.run(["git", "add", "sdk/prettier/index.js"], cwd=repo_root, check=True)
            subprocess.run(["git", "commit", "-m", "Update Prettier support (#11)"], cwd=repo_root, check=True)

            release_commits = release_commits_since_last_bump(repo_root)
            changed_paths = changed_paths_for_commits(repo_root, release_commits)

            self.assertEqual(
                [commit.subject for commit in release_commits],
                ["Add Python client (#10)", "Update Prettier support (#11)"],
            )
            self.assertEqual(
                [commit.pr_number for commit in release_commits],
                [10, 11],
            )
            self.assertEqual(
                changed_paths,
                ["lib/py/client.py", "sdk/prettier/index.js"],
            )


if __name__ == "__main__":
    unittest.main()
