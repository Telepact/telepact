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

from click.testing import CliRunner
import click

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_ROOT))

from telepact_project_cli.cli import main
from telepact_project_cli.commands.doc_versions import _latest_released_versions
from telepact_project_cli.release_plan import (
    compute_release_manifest,
    load_release_manifest,
    resolve_publish_targets,
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

    def test_publish_targets_requires_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            (repo_root / "VERSION.txt").write_text("1.0.0-alpha.214", encoding="utf-8")

            with self.assertRaises(click.ClickException):
                resolve_publish_targets(repo_root, release_tag="1.0.0-alpha.214")

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

    def test_bump_commit_message_is_manifest_only_and_can_request_skip_build(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            (repo_root / "VERSION.txt").write_text("1.0.0-alpha.214", encoding="utf-8")
            (repo_root / ".release").mkdir()
            (repo_root / ".release" / "release-targets.yaml").write_text(
                textwrap.dedent(
                    """
                    projects:
                      ts:
                        paths: [lib/ts]
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )
            (repo_root / "lib" / "go").mkdir(parents=True)
            (repo_root / "lib" / "go" / "go.mod").write_text(
                "module github.com/example/telepact/lib/go\n\ngo 1.22\n",
                encoding="utf-8",
            )
            (repo_root / "lib" / "java").mkdir(parents=True)
            (repo_root / "lib" / "java" / "pom.xml").write_text(
                textwrap.dedent(
                    """
                    <project xmlns="http://maven.apache.org/POM/4.0.0">
                      <modelVersion>4.0.0</modelVersion>
                      <groupId>io.github.example</groupId>
                      <artifactId>telepact</artifactId>
                      <version>1.0.0-alpha.214</version>
                    </project>
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )
            (repo_root / "lib" / "py").mkdir(parents=True)
            (repo_root / "lib" / "py" / "pyproject.toml").write_text(
                textwrap.dedent(
                    """
                    [project]
                    name = "telepact"
                    version = "1.0.0-alpha.214"
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )
            (repo_root / "lib" / "ts").mkdir(parents=True)
            (repo_root / "lib" / "ts" / "package.json").write_text(
                json.dumps({"name": "telepact", "version": "1.0.0-alpha.214"}, indent=2) + "\n",
                encoding="utf-8",
            )
            (repo_root / "sdk" / "cli").mkdir(parents=True)
            (repo_root / "sdk" / "cli" / "pyproject.toml").write_text(
                textwrap.dedent(
                    """
                    [project]
                    name = "telepact-cli"
                    version = "1.0.0-alpha.214"
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )
            (repo_root / "sdk" / "console").mkdir(parents=True)
            (repo_root / "sdk" / "console" / "package.json").write_text(
                json.dumps({"name": "telepact-console", "version": "1.0.0-alpha.214"}, indent=2) + "\n",
                encoding="utf-8",
            )
            (repo_root / "sdk" / "prettier").mkdir(parents=True)
            (repo_root / "sdk" / "prettier" / "package.json").write_text(
                json.dumps({"name": "prettier-plugin-telepact", "version": "1.0.0-alpha.214"}, indent=2) + "\n",
                encoding="utf-8",
            )

            subprocess.run(["git", "init"], cwd=repo_root, check=True, capture_output=True, text=True)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_root, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo_root, check=True)
            subprocess.run(["git", "add", "."], cwd=repo_root, check=True)
            subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_root, check=True)

            runner = CliRunner()
            with _pushd(repo_root):
                result = runner.invoke(
                    main,
                    ["bump"],
                    env={
                        "PR_NUMBER": "42",
                        "TELEPACT_BUMP_SKIP_BUILD": "true",
                    },
                )

            self.assertEqual(result.exit_code, 0, msg=result.output)
            commit_subject = subprocess.run(
                ["git", "show", "-s", "--format=%s", "HEAD"],
                cwd=repo_root,
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            commit_body = subprocess.run(
                ["git", "show", "-s", "--format=%b", "HEAD"],
                cwd=repo_root,
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()

            self.assertEqual(commit_subject, "Bump version to 1.0.0-alpha.215 (#42) [skip build]")
            self.assertEqual(commit_body, "")

    def test_should_skip_build_command_detects_phrase(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            (repo_root / "VERSION.txt").write_text("1.0.0-alpha.214", encoding="utf-8")
            subprocess.run(["git", "init"], cwd=repo_root, check=True, capture_output=True, text=True)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_root, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo_root, check=True)
            (repo_root / "README.md").write_text("hello\n", encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=repo_root, check=True)
            subprocess.run(
                ["git", "commit", "-m", "Bump version to 1.0.0-alpha.215 (#42) [skip build]"],
                cwd=repo_root,
                check=True,
            )

            output_path = repo_root / "github-output.txt"
            runner = CliRunner()
            with _pushd(repo_root):
                result = runner.invoke(
                    main,
                    ["should-skip-build", "--github-output", str(output_path)],
                )

            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertEqual(output_path.read_text(encoding="utf-8"), "skip_build=true\n")


if __name__ == "__main__":
    unittest.main()
