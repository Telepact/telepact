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
from types import SimpleNamespace
from unittest.mock import Mock, patch

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


class AutoMergeWorkflowTests(unittest.TestCase):
    def test_verify_automerge_conditions_rejects_non_collaborator(self) -> None:
        repo = Mock(full_name="Telepact/telepact")
        repo.has_in_collaborators.return_value = False
        pr = SimpleNamespace(
            state="open",
            base=SimpleNamespace(ref="main"),
            head=SimpleNamespace(repo=SimpleNamespace(full_name="Telepact/telepact")),
        )

        runner = CliRunner()
        with patch(
            "telepact_project_cli.cli._get_repo_and_pr",
            return_value=(None, repo, pr, 16),
        ):
            result = runner.invoke(
                main,
                ["verify-automerge-conditions"],
                env={"COMMENT_AUTHOR": "octocat"},
            )

        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("is not a collaborator", result.output)

    def test_verify_automerge_conditions_rejects_insufficient_permission(self) -> None:
        repo = Mock(full_name="Telepact/telepact")
        repo.has_in_collaborators.return_value = True
        repo.get_collaborator_permission.return_value = "read"
        pr = SimpleNamespace(
            state="open",
            base=SimpleNamespace(ref="main"),
            head=SimpleNamespace(repo=SimpleNamespace(full_name="Telepact/telepact")),
        )

        runner = CliRunner()
        with patch(
            "telepact_project_cli.cli._get_repo_and_pr",
            return_value=(None, repo, pr, 17),
        ):
            result = runner.invoke(
                main,
                ["verify-automerge-conditions"],
                env={"COMMENT_AUTHOR": "octocat"},
            )

        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("does not have merge permission", result.output)

    def test_verify_automerge_conditions_rejects_fork_pull_request(self) -> None:
        repo = Mock(full_name="Telepact/telepact")
        pr = SimpleNamespace(
            state="open",
            base=SimpleNamespace(ref="main"),
            head=SimpleNamespace(repo=SimpleNamespace(full_name="someone/fork")),
        )

        runner = CliRunner()
        with patch(
            "telepact_project_cli.cli._get_repo_and_pr",
            return_value=(None, repo, pr, 17),
        ):
            result = runner.invoke(
                main,
                ["verify-automerge-conditions"],
                env={"COMMENT_AUTHOR": "octocat"},
            )

        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("must use a branch", result.output)

    def test_tidy_pr_marks_ready_and_updates_branch_when_behind(self) -> None:
        repo = Mock(full_name="Telepact/telepact")
        repo.compare.return_value = SimpleNamespace(behind_by=2)

        initial_pr = Mock()
        initial_pr.state = "open"
        initial_pr.draft = True
        initial_pr.base = SimpleNamespace(ref="main", sha="base-sha")
        initial_pr.head = SimpleNamespace(
            sha="head-sha",
            repo=SimpleNamespace(full_name="Telepact/telepact"),
        )

        ready_pr = Mock()
        ready_pr.state = "open"
        ready_pr.draft = False
        ready_pr.base = initial_pr.base
        ready_pr.head = initial_pr.head

        updated_pr = Mock()
        updated_pr.state = "open"
        updated_pr.draft = False
        updated_pr.base = initial_pr.base
        updated_pr.head = SimpleNamespace(
            sha="updated-head-sha",
            repo=SimpleNamespace(full_name="Telepact/telepact"),
        )

        runner = CliRunner()
        with patch(
            "telepact_project_cli.cli._get_repo_and_pr",
            return_value=(None, repo, initial_pr, 18),
        ), patch(
            "telepact_project_cli.cli._refresh_pull_request",
            side_effect=[ready_pr, updated_pr],
        ), patch(
            "telepact_project_cli.cli.time.sleep",
            return_value=None,
        ):
            result = runner.invoke(main, ["tidy-pr"])

        self.assertEqual(result.exit_code, 0, msg=result.output)
        initial_pr.mark_ready_for_review.assert_called_once_with()
        ready_pr.update_branch.assert_called_once_with(expected_head_sha="head-sha")

    def test_tidy_pr_leaves_ready_up_to_date_pull_request_alone(self) -> None:
        repo = Mock(full_name="Telepact/telepact")
        repo.compare.return_value = SimpleNamespace(behind_by=0)

        pr = Mock()
        pr.state = "open"
        pr.draft = False
        pr.base = SimpleNamespace(ref="main", sha="base-sha")
        pr.head = SimpleNamespace(
            sha="head-sha",
            repo=SimpleNamespace(full_name="Telepact/telepact"),
        )

        runner = CliRunner()
        with patch(
            "telepact_project_cli.cli._get_repo_and_pr",
            return_value=(None, repo, pr, 18),
        ):
            result = runner.invoke(main, ["tidy-pr"])

        self.assertEqual(result.exit_code, 0, msg=result.output)
        pr.mark_ready_for_review.assert_not_called()
        pr.update_branch.assert_not_called()

    def test_verify_pr_requirements_fails_when_head_changes_while_waiting(self) -> None:
        repo = Mock(full_name="Telepact/telepact")
        repo.get_branch.return_value.get_required_status_checks.return_value.contexts = []

        initial_pr = SimpleNamespace(
            state="open",
            base=SimpleNamespace(ref="main"),
            head=SimpleNamespace(
                sha="head-sha",
                repo=SimpleNamespace(full_name="Telepact/telepact"),
            ),
            mergeable_state="unknown",
        )
        changed_pr = SimpleNamespace(
            state="open",
            base=initial_pr.base,
            head=SimpleNamespace(
                sha="new-head-sha",
                repo=SimpleNamespace(full_name="Telepact/telepact"),
            ),
            mergeable_state="clean",
        )

        runner = CliRunner()
        with patch(
            "telepact_project_cli.cli._get_repo_and_pr",
            return_value=(None, repo, initial_pr, 19),
        ), patch(
            "telepact_project_cli.cli._refresh_pull_request",
            side_effect=[initial_pr, changed_pr],
        ), patch("telepact_project_cli.cli.time.sleep", return_value=None):
            result = runner.invoke(main, ["verify-pr-requirements"])

        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("head changed", result.output)

    def test_bump_commits_changes_via_git_data_api(self) -> None:
        repo = Mock(full_name="Telepact/telepact")
        pr = Mock()
        pr.state = "open"
        pr.base = SimpleNamespace(ref="main")
        pr.head = SimpleNamespace(
            ref="feature-branch",
            sha="head-sha",
            repo=SimpleNamespace(full_name="Telepact/telepact"),
        )
        pr.get_files.return_value = [SimpleNamespace(filename="lib/py/pyproject.toml")]

        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            manifest_path = Path(".release/release-manifest.json")

            (repo_root / "VERSION.txt").write_text("1.2.3", encoding="utf-8")
            (repo_root / ".release").mkdir()

            def _fake_write_release_manifest(_repo_root: Path, _manifest) -> Path:
                path = _repo_root / manifest_path
                path.write_text('{"version":"1.2.4"}\n', encoding="utf-8")
                return path

            def _fake_write_doc_versions(_repo_root: Path, *_args, **_kwargs) -> Path:
                path = _repo_root / "doc-versions.json"
                path.write_text('{"version":"1.2.4"}\n', encoding="utf-8")
                return path

            with patch(
                "telepact_project_cli.cli._get_repo_and_pr",
                return_value=(None, repo, pr, 20),
            ), patch(
                "telepact_project_cli.cli._sync_pull_request_head_to_worktree",
            ), patch(
                "telepact_project_cli.cli.compute_release_manifest",
                return_value=SimpleNamespace(targets=("py",)),
            ), patch(
                "telepact_project_cli.cli.write_release_manifest",
                side_effect=_fake_write_release_manifest,
            ), patch(
                "telepact_project_cli.cli.write_doc_versions",
                side_effect=_fake_write_doc_versions,
            ), patch(
                "telepact_project_cli.cli._commit_files_via_git_data_api",
                return_value="new-commit-sha",
            ) as commit_files, patch(
                "telepact_project_cli.cli.subprocess.run"
            ) as subprocess_run, _pushd(repo_root):
                result = runner.invoke(main, ["bump"])
                self.assertEqual(result.exit_code, 0, msg=result.output)
                commit_files.assert_called_once()
                _, branch_name, head_sha, edited_files, commit_message = commit_files.call_args.args
                self.assertEqual(branch_name, "feature-branch")
                self.assertEqual(head_sha, "head-sha")
                self.assertEqual(
                    edited_files,
                    ["VERSION.txt", ".release/release-manifest.json", "doc-versions.json"],
                )
                self.assertEqual(commit_message, "Bump version to 1.2.4 (#20)")
                self.assertEqual(subprocess_run.call_count, 0)

    def test_bump_fails_when_version_file_is_missing(self) -> None:
        repo = Mock(full_name="Telepact/telepact")
        pr = Mock()
        pr.state = "open"
        pr.base = SimpleNamespace(ref="main")
        pr.head = SimpleNamespace(
            ref="feature-branch",
            sha="head-sha",
            repo=SimpleNamespace(full_name="Telepact/telepact"),
        )

        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)

            with patch(
                "telepact_project_cli.cli._get_repo_and_pr",
                return_value=(None, repo, pr, 21),
            ), patch(
                "telepact_project_cli.cli._sync_pull_request_head_to_worktree",
            ), _pushd(repo_root):
                result = runner.invoke(main, ["bump"])

        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("Version file VERSION.txt does not exist", result.output)

    def test_merge_pr_squashes_pull_request(self) -> None:
        repo = Mock(full_name="Telepact/telepact")
        pr = Mock()
        pr.state = "open"
        pr.base = SimpleNamespace(ref="main")
        pr.head = SimpleNamespace(
            sha="head-sha",
            repo=SimpleNamespace(full_name="Telepact/telepact"),
        )
        pr.merge.return_value = SimpleNamespace(merged=True, message="merged")

        runner = CliRunner()
        with patch(
            "telepact_project_cli.cli._get_repo_and_pr",
            return_value=(None, repo, pr, 22),
        ):
            result = runner.invoke(main, ["merge-pr"])

        self.assertEqual(result.exit_code, 0, msg=result.output)
        pr.merge.assert_called_once_with(
            merge_method="squash",
            sha="head-sha",
            delete_branch=False,
        )


if __name__ == "__main__":
    unittest.main()
