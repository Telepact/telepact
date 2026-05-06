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
from unittest import mock

from click.testing import CliRunner

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_ROOT))

from telepact_project_cli.cli import main
from telepact_project_cli.commands.doc_versions import _latest_released_versions
from telepact_project_cli.release_plan import (
    ReleaseComparison,
    changed_paths_for_release_comparison,
    changed_paths_since_last_version_change,
    compute_release_manifest,
    compute_release_manifest_for_comparison,
    compute_release_manifest_from_git,
    read_release_manifest,
    render_release_manifest_for_stdout,
)


@contextlib.contextmanager
def _pushd(path: Path):
    old_cwd = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old_cwd)


def _run_git(repo_root: Path, *args: str) -> str:
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
    _run_git(repo_root, "init")
    _run_git(repo_root, "config", "user.name", "Test User")
    _run_git(repo_root, "config", "user.email", "test@example.com")


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
    _run_git(repo_root, "add", ".")
    _run_git(repo_root, "commit", "-m", message)


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

    def test_set_version_updates_package_lock_from_current_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = Path(tmp_dir)
            (project_root / "package.json").write_text(
                '{\n  "name": "example",\n  "version": "1.2.3"\n}\n',
                encoding="utf-8",
            )
            (project_root / "package-lock.json").write_text("{}", encoding="utf-8")

            runner = CliRunner()
            with (
                _pushd(project_root),
                mock.patch("telepact_project_cli.commands.project_version.subprocess.run") as run,
            ):
                result = runner.invoke(main, ["set-version", "1.2.4"])

            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertEqual(json.loads((project_root / "package.json").read_text(encoding="utf-8"))["version"], "1.2.4")
            run.assert_called_once_with(["npm", "install"], cwd=Path("."), check=True)
            self.assertIn("Updated package-lock.json in .", result.output)

    def test_set_version_updates_uv_lock_from_current_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = Path(tmp_dir)
            (project_root / "pyproject.toml").write_text(
                textwrap.dedent(
                    """
                    [project]
                    name = "example"
                    version = "1.2.3"
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )
            (project_root / "uv.lock").write_text("version = 1\n", encoding="utf-8")

            runner = CliRunner()
            with (
                _pushd(project_root),
                mock.patch("telepact_project_cli.commands.project_version.subprocess.run") as run,
            ):
                result = runner.invoke(main, ["set-version", "1.2.4"])

            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertIn('version = "1.2.4"', (project_root / "pyproject.toml").read_text(encoding="utf-8"))
            run.assert_called_once_with(["uv", "lock"], cwd=Path("."), check=True)
            self.assertIn("Updated uv.lock in .", result.output)

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
                comparison=ReleaseComparison(base_commit="abc123", head_commit="def456"),
            )

            self.assertEqual(manifest.comparison, ReleaseComparison(base_commit="abc123", head_commit="def456"))
            self.assertEqual(manifest.direct_targets, ("prettier", "ts"))
            self.assertEqual(manifest.targets, ("console", "dart", "prettier", "ts"))
            self.assertEqual(
                manifest.changed_paths,
                ("README.md", "lib/ts/src/main.ts", "sdk/prettier/package.json"),
            )

    def test_render_release_manifest_for_stdout_returns_sorted_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            (repo_root / "VERSION.txt").write_text("1.0.0-alpha.214", encoding="utf-8")
            _write_release_targets(repo_root)

            manifest = compute_release_manifest(
                repo_root,
                changed_paths=["sdk/prettier/package.json", "lib/ts/src/main.ts"],
                version="1.0.0-alpha.215",
                pr_number=None,
                comparison=ReleaseComparison(base_commit="abc123", head_commit="def456"),
            )

            rendered = render_release_manifest_for_stdout(manifest)

            self.assertEqual(
                json.loads(rendered),
                {
                    "changed_paths": ["lib/ts/src/main.ts", "sdk/prettier/package.json"],
                    "comparison": {"base_commit": "abc123", "head_commit": "def456"},
                    "direct_targets": ["prettier", "ts"],
                    "pr_number": None,
                    "targets": ["console", "dart", "prettier", "ts"],
                    "version": "1.0.0-alpha.215",
                },
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
            _commit_all(repo_root, "Bump version")

            self.assertEqual(
                changed_paths_since_last_version_change(repo_root),
                ["lib/py/impl.py"],
            )

    def test_changed_paths_for_release_comparison_uses_exact_commits(self) -> None:
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

            self.assertEqual(
                changed_paths_for_release_comparison(
                    repo_root,
                    ReleaseComparison(
                        base_commit=_run_git(repo_root, "rev-parse", "HEAD~1"),
                        head_commit=_run_git(repo_root, "rev-parse", "HEAD"),
                    ),
                ),
                ["lib/py/impl.py"],
            )

    def test_changed_paths_since_last_version_change_filters_version_file_from_git_diff(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            (repo_root / "VERSION.txt").write_text("1.0.0-alpha.214", encoding="utf-8")
            _write_release_targets(repo_root)

            with mock.patch(
                "telepact_project_cli.release_plan._version_change_commits",
                side_effect=[["head", "previous"], ["previous"]],
            ), mock.patch(
                "telepact_project_cli.release_plan._resolved_commit_sha",
                return_value="not-a-version-commit",
            ), mock.patch(
                "telepact_project_cli.release_plan._git_stdout",
                side_effect=["parent", "VERSION.txt\nlib/py/impl.py\n"],
            ):
                self.assertEqual(
                    changed_paths_since_last_version_change(repo_root),
                    ["lib/py/impl.py"],
                )

    def test_changed_paths_since_last_version_change_excludes_head_before_finding_latest_version_commit(self) -> None:
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

            (repo_root / "lib" / "py" / "feature_before_bump.py").write_text("print('before')\n", encoding="utf-8")
            _commit_all(repo_root, "Feature before bump")

            (repo_root / "VERSION.txt").write_text("1.0.0-alpha.201", encoding="utf-8")
            (repo_root / "lib" / "py" / "pyproject.toml").write_text(
                '[project]\nname = "telepact"\nversion = "1.0.0-alpha.201"\n',
                encoding="utf-8",
            )
            _commit_all(repo_root, "Bump version")

            (repo_root / "lib" / "py" / "feature_after_bump.py").write_text("print('after')\n", encoding="utf-8")
            _commit_all(repo_root, "Feature after bump")

            self.assertEqual(
                changed_paths_since_last_version_change(repo_root),
                ["lib/py/feature_after_bump.py"],
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
            initial_release_commit = _run_git(repo_root, "rev-parse", "HEAD~2")
            feature_commit = _run_git(repo_root, "rev-parse", "HEAD~1")

            self.assertEqual(manifest.version, "1.0.0-alpha.201")
            self.assertEqual(
                manifest.comparison,
                ReleaseComparison(base_commit=initial_release_commit, head_commit=feature_commit),
            )
            self.assertEqual(manifest.direct_targets, ("py",))
            self.assertEqual(manifest.targets, ("cli", "py"))
            self.assertEqual(manifest.changed_paths, ("lib/py/impl.py",))

    def test_compute_release_manifest_for_comparison_uses_comparison_for_targets(self) -> None:
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

            comparison = ReleaseComparison(
                base_commit=_run_git(repo_root, "rev-parse", "HEAD~1"),
                head_commit=_run_git(repo_root, "rev-parse", "HEAD"),
            )

            manifest = compute_release_manifest_for_comparison(
                repo_root,
                comparison=comparison,
                version="1.0.0-alpha.201",
                pr_number=17,
            )

            self.assertEqual(manifest.comparison, comparison)
            self.assertEqual(manifest.pr_number, 17)
            self.assertEqual(manifest.changed_paths, ("lib/py/impl.py",))
            self.assertEqual(manifest.direct_targets, ("py",))
            self.assertEqual(manifest.targets, ("cli", "py"))

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
                        "print-release-manifest",
                    ],
                )

            self.assertEqual(result.exit_code, 0, msg=result.output)
            manifest_path = repo_root / "release-manifest.json"
            manifest_path.write_text(result.output, encoding="utf-8")

            with _pushd(repo_root):
                result = runner.invoke(
                    main,
                    [
                        "publish-targets",
                        "--release-tag",
                        "1.0.0-alpha.215",
                        "--release-manifest-path",
                        str(manifest_path),
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

    def test_print_release_manifest_command_writes_manifest_to_stdout(self) -> None:
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

            runner = CliRunner()
            with _pushd(repo_root):
                result = runner.invoke(main, ["print-release-manifest"])

            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertEqual(
                json.loads(result.output),
                {
                    "changed_paths": ["lib/py/impl.py"],
                    "comparison": {
                        "base_commit": _run_git(repo_root, "rev-parse", "HEAD~2"),
                        "head_commit": _run_git(repo_root, "rev-parse", "HEAD~1"),
                    },
                    "direct_targets": ["py"],
                    "pr_number": None,
                    "targets": ["cli", "py"],
                    "version": "1.0.0-alpha.215",
                },
            )

    def test_read_release_manifest_reads_json_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            manifest_path = Path(tmp_dir) / "release-manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "version": "1.0.0-alpha.215",
                        "pr_number": 7,
                        "comparison": {"base_commit": "abc123", "head_commit": "def456"},
                        "changed_paths": ["lib/py/impl.py"],
                        "direct_targets": ["py"],
                        "targets": ["cli", "py"],
                    }
                ),
                encoding="utf-8",
            )

            manifest = read_release_manifest(manifest_path)

            self.assertEqual(manifest.version, "1.0.0-alpha.215")
            self.assertEqual(manifest.pr_number, 7)
            self.assertEqual(manifest.comparison, ReleaseComparison(base_commit="abc123", head_commit="def456"))
            self.assertEqual(manifest.changed_paths, ("lib/py/impl.py",))
            self.assertEqual(manifest.direct_targets, ("py",))
            self.assertEqual(manifest.targets, ("cli", "py"))

    def test_read_release_manifest_allows_null_comparison_base_commit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            manifest_path = Path(tmp_dir) / "release-manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "version": "1.0.0-alpha.215",
                        "pr_number": None,
                        "comparison": {"base_commit": None, "head_commit": "def456"},
                        "changed_paths": ["lib/py/impl.py"],
                        "direct_targets": ["py"],
                        "targets": ["cli", "py"],
                    }
                ),
                encoding="utf-8",
            )

            manifest = read_release_manifest(manifest_path)

            self.assertEqual(manifest.comparison, ReleaseComparison(base_commit=None, head_commit="def456"))

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
                    "telepact_project_cli.commands.project_version._release_comparison_since_main",
                    return_value=ReleaseComparison(base_commit="abc123", head_commit="def456"),
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
                    "telepact_project_cli.commands.project_version._release_comparison_since_main",
                    return_value=ReleaseComparison(base_commit="abc123", head_commit="def456"),
                ),
            ):
                result = runner.invoke(main, ["bump"])

            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertEqual((repo_root / "VERSION.txt").read_text(encoding="utf-8"), "1.0.0-alpha.214")

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
