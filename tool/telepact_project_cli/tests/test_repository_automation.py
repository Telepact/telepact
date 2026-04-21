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
import textwrap
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from click.testing import CliRunner

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_ROOT))

from telepact_project_cli.cli import main
from telepact_project_cli.commands.project_version import _create_git_data_commit
from telepact_project_cli.commands.repository_automation import PullRequestState


@contextlib.contextmanager
def _pushd(path: Path):
    old_cwd = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old_cwd)


class _FakeGitRef:
    def __init__(self, sha: str):
        self.object = SimpleNamespace(sha=sha)
        self.edited_to: tuple[str, bool] | None = None

    def edit(self, sha: str, force: bool = False) -> None:
        self.edited_to = (sha, force)
        self.object.sha = sha


class _FakeGitCommit:
    def __init__(self, sha: str):
        self.sha = sha
        self.tree = object()


class _FakeRepo:
    def __init__(self, head_sha: str, head_ref: str, changed_paths: list[str]):
        self._ref = _FakeGitRef(head_sha)
        self._base_commit = _FakeGitCommit(head_sha)
        self._new_commit = _FakeGitCommit("new-commit-sha")
        self._pull = SimpleNamespace(
            head=SimpleNamespace(sha=head_sha, ref=head_ref),
            get_files=lambda: [SimpleNamespace(filename=path) for path in changed_paths],
        )
        self.created_tree = None
        self.created_commit_message = None

    def get_pull(self, _pr_number: int):
        return self._pull

    def get_git_ref(self, _name: str):
        return self._ref

    def get_git_commit(self, _sha: str):
        return self._base_commit

    def create_git_tree(self, tree, base_tree):
        self.created_tree = (tree, base_tree)
        return object()

    def create_git_commit(self, message, tree, parents):
        self.created_commit_message = message
        self.created_commit_parents = parents
        return self._new_commit


class _FakeGithub:
    def __init__(self, repo: _FakeRepo):
        self._repo = repo

    def get_repo(self, _repository: str):
        return self._repo


class RepositoryAutomationTests(unittest.TestCase):
    def test_verify_merge_conditions_rejects_insufficient_permission(self) -> None:
        runner = CliRunner()
        with patch.dict(
            os.environ,
            {
                "COMMENTER_LOGIN": "reader",
                "GITHUB_REPOSITORY": "Telepact/telepact",
                "GITHUB_TOKEN": "token",
                "PR_NUMBER": "12",
            },
            clear=False,
        ):
            with patch(
                "telepact_project_cli.commands.repository_automation._load_collaborator_permission",
                return_value="read",
            ):
                result = runner.invoke(main, ["verify-merge-conditions"])

        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("does not have merge permission", result.output)

    def test_verify_pr_requirements_writes_locked_head_output(self) -> None:
        runner = CliRunner()
        verified_state = PullRequestState(
            number=12,
            title="Example",
            state="open",
            merged=False,
            draft=False,
            base_ref="main",
            head_ref="copilot/test",
            head_sha="locked-head",
            mergeable=True,
            mergeable_state="clean",
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "github-output.txt"
            with patch.dict(
                os.environ,
                {
                    "GITHUB_REPOSITORY": "Telepact/telepact",
                    "GITHUB_TOKEN": "token",
                    "PR_NUMBER": "12",
                },
                clear=False,
            ):
                with patch(
                    "telepact_project_cli.commands.repository_automation._wait_for_stable_pull_request_state",
                    return_value=verified_state,
                ), patch(
                    "telepact_project_cli.commands.repository_automation._verify_build_requirements",
                    return_value=verified_state,
                ):
                    result = runner.invoke(
                        main,
                        [
                            "verify-pr-requirements",
                            "--expected-head-sha",
                            "locked-head",
                            "--github-output",
                            str(output_path),
                        ],
                    )

            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertEqual(
                output_path.read_text(encoding="utf-8").splitlines(),
                [
                    "head_sha=locked-head",
                    "head_ref=copilot/test",
                    "base_ref=main",
                ],
            )

    def test_create_git_data_commit_updates_branch_ref_without_git_cli(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            updated_file = repo_root / "VERSION.txt"
            updated_file.write_text("1.2.4\n", encoding="utf-8")

            fake_repo = _FakeRepo(head_sha="base-sha", head_ref="copilot/test", changed_paths=["lib/ts/package.json"])
            new_sha = _create_git_data_commit(
                repo_root,
                fake_repo,
                "copilot/test",
                "base-sha",
                "Bump version to 1.2.4 (#12)",
                ["VERSION.txt"],
            )

            self.assertEqual(new_sha, "new-commit-sha")
            self.assertEqual(fake_repo._ref.edited_to, ("new-commit-sha", False))
            self.assertEqual(fake_repo.created_commit_message, "Bump version to 1.2.4 (#12)")
            self.assertEqual(len(fake_repo.created_tree[0]), 1)

    def test_bump_commits_with_git_data_api_and_updates_outputs(self) -> None:
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            (repo_root / "VERSION.txt").write_text("1.0.0-alpha.1", encoding="utf-8")
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
            (repo_root / "lib/go").mkdir(parents=True)
            (repo_root / "lib/go/go.mod").write_text("module example.com/telepact\n", encoding="utf-8")
            (repo_root / "lib/java").mkdir(parents=True)
            (repo_root / "lib/java/pom.xml").write_text(
                "<project xmlns=\"http://maven.apache.org/POM/4.0.0\"><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>java</artifactId><version>1.0.0-alpha.1</version></project>",
                encoding="utf-8",
            )
            (repo_root / "lib/py").mkdir(parents=True)
            (repo_root / "lib/py/pyproject.toml").write_text(
                "[project]\nname = \"telepact-py\"\nversion = \"1.0.0-alpha.1\"\n",
                encoding="utf-8",
            )
            (repo_root / "lib/ts").mkdir(parents=True)
            (repo_root / "lib/ts/package.json").write_text('{"name":"telepact-ts","version":"1.0.0-alpha.1"}\n', encoding="utf-8")
            (repo_root / "bind/dart").mkdir(parents=True)
            (repo_root / "bind/dart/pubspec.yaml").write_text("name: telepact_dart\nversion: 1.0.0-alpha.1\n", encoding="utf-8")
            (repo_root / "bind/dart/package.json").write_text('{"name":"telepact-dart","version":"1.0.0-alpha.1"}\n', encoding="utf-8")
            (repo_root / "sdk/cli").mkdir(parents=True)
            (repo_root / "sdk/cli/pyproject.toml").write_text(
                "[project]\nname = \"telepact-cli\"\nversion = \"1.0.0-alpha.1\"\n",
                encoding="utf-8",
            )
            (repo_root / "sdk/prettier").mkdir(parents=True)
            (repo_root / "sdk/prettier/package.json").write_text(
                '{"name":"telepact-prettier","version":"1.0.0-alpha.1"}\n',
                encoding="utf-8",
            )
            (repo_root / "sdk/console").mkdir(parents=True)
            (repo_root / "sdk/console/package.json").write_text(
                '{"name":"telepact-console","version":"1.0.0-alpha.1"}\n',
                encoding="utf-8",
            )
            (repo_root / "doc/04-operate").mkdir(parents=True)
            (repo_root / "doc/04-operate/03-versions.md").write_text(
                textwrap.dedent(
                    """
                    # Versions

                    | Kind | Package | Registry | Version |
                    |---|---|---|---|
                    | Library (Go) | `example.com/telepact` | Go module (proxy.golang.org) | `v1.0.0-alpha.1` |
                    | Library (Java) | `example:java` | Maven Central | `1.0.0-alpha.1` |
                    | Library (Python) | `telepact-py` | PyPI | `1.0.0a1` |
                    | Library (TypeScript) | `telepact-ts` | npm | `1.0.0-alpha.1` |
                    | SDK (CLI) | `telepact-cli` | PyPI | `1.0.0a1` |
                    | SDK (Console) | `telepact-console` | npm | `1.0.0-alpha.1` |
                    | SDK (Prettier) | `telepact-prettier` | npm | `1.0.0-alpha.1` |
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )

            fake_repo = _FakeRepo(head_sha="base-sha", head_ref="copilot/test", changed_paths=["lib/ts/src/index.ts"])
            output_path = repo_root / "github-output.txt"
            with patch.dict(
                os.environ,
                {
                    "GITHUB_REPOSITORY": "Telepact/telepact",
                    "GITHUB_TOKEN": "token",
                    "PR_NUMBER": "12",
                },
                clear=False,
            ):
                with patch("telepact_project_cli.commands.project_version.Github", return_value=_FakeGithub(fake_repo)):
                    with _pushd(repo_root):
                        result = runner.invoke(
                            main,
                            [
                                "bump",
                                "--expected-head-sha",
                                "base-sha",
                                "--github-output",
                                str(output_path),
                            ],
                        )

            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertIn("head_sha=new-commit-sha", output_path.read_text(encoding="utf-8"))
            self.assertIn("version=1.0.0-alpha.2", output_path.read_text(encoding="utf-8"))
            self.assertEqual((repo_root / "VERSION.txt").read_text(encoding="utf-8"), "1.0.0-alpha.2")
            self.assertTrue((repo_root / ".release/release-manifest.json").exists())
            self.assertEqual(fake_repo._ref.edited_to, ("new-commit-sha", False))
            self.assertIn("Bump version to 1.0.0-alpha.2 (#12)", fake_repo.created_commit_message)


if __name__ == "__main__":
    unittest.main()
