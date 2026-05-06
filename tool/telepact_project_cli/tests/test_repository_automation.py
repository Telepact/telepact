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
import sys
import tempfile
import unittest
import os
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_ROOT))

from click.testing import CliRunner

from telepact_project_cli.cli import main
from telepact_project_cli.commands.repository_automation import (
    _build_release_body,
    _combined_status_state,
    _process_merge_ready_pull_request,
    _pull_request_ci_state,
    _validate_merge_request,
    _verify_pull_request_ci,
    _wait_for_pr_stable,
)


@contextlib.contextmanager
def _pushd(path: Path):
    old_cwd = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old_cwd)


class RepositoryAutomationTests(unittest.TestCase):
    def test_release_command_does_not_upload_release_manifest_asset(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            from test_release_plan import _commit_all, _init_repo, _pushd, _write_release_targets

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

            uploaded_assets: dict[str, str] = {}

            def _upload_asset(*, path: str, name: str, label: str) -> None:
                uploaded_assets[name] = Path(path).read_text(encoding="utf-8")

            release_obj = mock.Mock(html_url="https://example.test/release/1")
            release_obj.upload_asset.side_effect = _upload_asset

            repo = mock.Mock()
            repo.create_git_release.return_value = release_obj
            github_client = mock.Mock()
            github_client.get_repo.return_value = repo

            runner = CliRunner()
            with (
                _pushd(repo_root),
                mock.patch("telepact_project_cli.commands.repository_automation.Github", return_value=github_client),
                mock.patch(
                    "telepact_project_cli.commands.repository_automation._release_pr_metadata",
                    return_value=("Release title", None, None),
                ),
                mock.patch("telepact_project_cli.commands.repository_automation._head_commit_subject", return_value="Release title"),
            ):
                result = runner.invoke(
                    main,
                    ["release"],
                    env={
                        "GITHUB_TOKEN": "token",
                        "GITHUB_REPOSITORY": "Telepact/telepact",
                    },
                )

            self.assertEqual(result.exit_code, 0, msg=result.output)
            repo.create_git_release.assert_called_once()
            release_obj.upload_asset.assert_not_called()
            self.assertEqual(uploaded_assets, {})

    def test_build_release_body_groups_commits_by_direct_release_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            from test_release_plan import _commit_all, _init_repo, _pushd, _write_release_targets

            _init_repo(repo_root)
            _write_release_targets(repo_root)
            (repo_root / "VERSION.txt").write_text("1.0.0-alpha.317", encoding="utf-8")
            (repo_root / "lib" / "py").mkdir(parents=True)
            (repo_root / "lib" / "py" / "pyproject.toml").write_text(
                """
[project]
name = "telepact"
version = "1.0.0-alpha.317"
""".strip()
                + "\n",
                encoding="utf-8",
            )
            (repo_root / "sdk" / "cli").mkdir(parents=True)
            (repo_root / "sdk" / "cli" / "pyproject.toml").write_text(
                """
[project]
name = "telepact-cli"
version = "1.0.0-alpha.317"
""".strip()
                + "\n",
                encoding="utf-8",
            )
            (repo_root / "site").mkdir(parents=True)
            (repo_root / "site" / "README.md").write_text("initial\n", encoding="utf-8")
            _commit_all(repo_root, "Initial release")

            (repo_root / "lib" / "py" / "impl.py").write_text("print('py')\n", encoding="utf-8")
            _commit_all(repo_root, "Add Python release feature")

            (repo_root / "site" / "README.md").write_text("updated\n", encoding="utf-8")
            _commit_all(repo_root, "Refresh website copy")

            (repo_root / "sdk" / "cli" / "cli.py").write_text("print('cli')\n", encoding="utf-8")
            _commit_all(repo_root, "Add CLI release feature")

            (repo_root / "VERSION.txt").write_text("1.0.0-alpha.318", encoding="utf-8")
            (repo_root / "lib" / "py" / "pyproject.toml").write_text(
                """
[project]
name = "telepact"
version = "1.0.0-alpha.318"
""".strip()
                + "\n",
                encoding="utf-8",
            )
            (repo_root / "sdk" / "cli" / "pyproject.toml").write_text(
                """
[project]
name = "telepact-cli"
version = "1.0.0-alpha.318"
""".strip()
                + "\n",
                encoding="utf-8",
            )
            _commit_all(repo_root, "Bump version")

            with _pushd(repo_root):
                body = _build_release_body(
                    repo_root,
                    pr_title="Improve release notes",
                    pr_number=7,
                    pr_url="https://github.com/Telepact/telepact/pull/7",
                    direct_targets=["cli", "py"],
                    release_targets=["cli", "py"],
                )

            self.assertIn("### Published targets", body)
            self.assertIn("### Library (Python) — `telepact` (PyPI)", body)
            self.assertIn("### SDK (CLI) — `telepact-cli` (PyPI)", body)
            self.assertIn("Add Python release feature", body)
            self.assertIn("Add CLI release feature", body)
            self.assertNotIn("Refresh website copy", body)
            self.assertNotIn("Bump version", body)

    def test_combined_status_state_reads_head_commit_status(self) -> None:
        pr = SimpleNamespace(
            head=SimpleNamespace(sha="head-sha"),
            base=SimpleNamespace(
                repo=SimpleNamespace(
                    get_commit=lambda sha: SimpleNamespace(
                        get_combined_status=lambda: SimpleNamespace(state="SUCCESS")
                    )
                )
            ),
        )

        self.assertEqual(_combined_status_state(pr), "success")

    def test_pull_request_ci_state_prefers_failed_check_runs(self) -> None:
        pr = SimpleNamespace(
            head=SimpleNamespace(sha="head-sha"),
            base=SimpleNamespace(
                repo=SimpleNamespace(
                    get_commit=lambda sha: SimpleNamespace(
                        get_combined_status=lambda: SimpleNamespace(state="pending"),
                        get_check_runs=lambda: [
                            SimpleNamespace(status="completed", conclusion="cancelled"),
                        ],
                    )
                )
            ),
        )

        self.assertEqual(_pull_request_ci_state(pr), "cancelled")

    def test_verify_pull_request_ci_fails_immediately_for_failed_check_run(self) -> None:
        pr = SimpleNamespace(
            number=7,
            head=SimpleNamespace(sha="head-sha"),
            base=SimpleNamespace(
                repo=SimpleNamespace(
                    get_commit=lambda sha: SimpleNamespace(
                        get_combined_status=lambda: SimpleNamespace(state="pending"),
                        get_check_runs=lambda: [
                            SimpleNamespace(status="completed", conclusion="failure"),
                        ],
                    )
                )
            ),
        )

        with mock.patch(
            "telepact_project_cli.commands.repository_automation._wait_for_pr_stable",
            return_value=pr,
        ):
            with self.assertRaisesRegex(RuntimeError, "CI failed with state 'failure'"):
                _verify_pull_request_ci(mock.Mock(), 7, "head-sha")

    def test_wait_for_pr_stable_rejects_closed_pull_request(self) -> None:
        repo = mock.Mock()
        repo.get_pull.return_value = SimpleNamespace(
            number=7,
            state="closed",
            head=SimpleNamespace(sha="head-sha"),
        )

        with self.assertRaisesRegex(RuntimeError, "Pull request #7 is not open."):
            _wait_for_pr_stable(repo, 7, "head-sha")

    def test_validate_merge_request_rejects_missing_reviews_for_non_admin(self) -> None:
        pr = SimpleNamespace(
            number=7,
            state="open",
            mergeable=True,
            mergeable_state="blocked",
            head=SimpleNamespace(sha="head-sha", repo=SimpleNamespace(full_name="Telepact/telepact")),
            base=SimpleNamespace(
                ref="main",
                repo=SimpleNamespace(
                    full_name="Telepact/telepact",
                    get_commit=lambda sha: SimpleNamespace(
                        get_combined_status=lambda: SimpleNamespace(state="success"),
                        get_check_runs=lambda: [SimpleNamespace(status="completed", conclusion="success")],
                    ),
                ),
            ),
        )

        with self.assertRaisesRegex(RuntimeError, "required approving reviews are missing"):
            _validate_merge_request(pr, is_admin=False)

    def test_validate_merge_request_allows_admin_when_only_reviews_are_missing(self) -> None:
        pr = SimpleNamespace(
            number=7,
            state="open",
            mergeable=True,
            mergeable_state="blocked",
            head=SimpleNamespace(sha="head-sha", repo=SimpleNamespace(full_name="Telepact/telepact")),
            base=SimpleNamespace(
                ref="main",
                repo=SimpleNamespace(
                    full_name="Telepact/telepact",
                    get_commit=lambda sha: SimpleNamespace(
                        get_combined_status=lambda: SimpleNamespace(state="success"),
                        get_check_runs=lambda: [SimpleNamespace(status="completed", conclusion="success")],
                    ),
                ),
            ),
        )

        _validate_merge_request(pr, is_admin=True)

    def test_mark_merge_ready_command_rejects_non_collaborator(self) -> None:
        repo = mock.Mock()
        repo.has_in_collaborators.return_value = False

        github_client = mock.Mock()
        github_client.get_repo.return_value = repo

        runner = CliRunner()
        with mock.patch("telepact_project_cli.commands.repository_automation.Github", return_value=github_client):
            result = runner.invoke(
                main,
                ["mark-merge-ready"],
                env={
                    "GITHUB_TOKEN": "token",
                    "GITHUB_REPOSITORY": "Telepact/telepact",
                    "COMMENTER_LOGIN": "outsider",
                    "PR_NUMBER": "7",
                },
            )

        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("not a repository collaborator", result.output)

    def test_mark_merge_ready_command_sets_skip_false_for_first_labeled_pr(self) -> None:
        issue = mock.Mock()
        issue.pull_request = object()
        issue.state = "open"
        issue.labels = []
        issue.add_to_labels = mock.Mock()

        repo = mock.Mock()
        repo.has_in_collaborators.return_value = True
        repo.get_collaborator_permission.return_value = "write"
        repo.get_issue.return_value = issue
        repo.get_label.return_value = mock.Mock()

        github_client = mock.Mock()
        github_client.get_repo.return_value = repo

        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmp_dir:
            github_output = Path(tmp_dir) / "github-output.txt"
            with (
                mock.patch("telepact_project_cli.commands.repository_automation.Github", return_value=github_client),
                mock.patch(
                    "telepact_project_cli.commands.repository_automation._open_merge_ready_pr_numbers",
                    return_value=[7],
                ),
            ):
                result = runner.invoke(
                    main,
                    ["mark-merge-ready", "--github-output", str(github_output)],
                    env={
                        "GITHUB_TOKEN": "token",
                        "GITHUB_REPOSITORY": "Telepact/telepact",
                        "COMMENTER_LOGIN": "writer",
                        "PR_NUMBER": "7",
                    },
                )

            self.assertEqual(result.exit_code, 0, msg=result.output)
            issue.add_to_labels.assert_called_once_with("Merge Ready")
            self.assertEqual(
                github_output.read_text(encoding="utf-8"),
                "skip_merge_loop=false\nmerge_ready_count=1\n",
            )

    def test_mark_merge_ready_command_sets_skip_true_when_multiple_prs_are_labeled(self) -> None:
        issue = mock.Mock()
        issue.pull_request = object()
        issue.state = "open"
        issue.labels = []
        issue.add_to_labels = mock.Mock()

        repo = mock.Mock()
        repo.has_in_collaborators.return_value = True
        repo.get_collaborator_permission.return_value = "write"
        repo.get_issue.return_value = issue
        repo.get_label.return_value = mock.Mock()

        github_client = mock.Mock()
        github_client.get_repo.return_value = repo

        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmp_dir:
            github_output = Path(tmp_dir) / "github-output.txt"
            with (
                mock.patch("telepact_project_cli.commands.repository_automation.Github", return_value=github_client),
                mock.patch(
                    "telepact_project_cli.commands.repository_automation._open_merge_ready_pr_numbers",
                    return_value=[7, 8],
                ),
            ):
                result = runner.invoke(
                    main,
                    ["mark-merge-ready", "--github-output", str(github_output)],
                    env={
                        "GITHUB_TOKEN": "token",
                        "GITHUB_REPOSITORY": "Telepact/telepact",
                        "COMMENTER_LOGIN": "writer",
                        "PR_NUMBER": "7",
                    },
                )

            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertEqual(
                github_output.read_text(encoding="utf-8"),
                "skip_merge_loop=true\nmerge_ready_count=2\n",
            )

    def test_open_version_bump_pr_does_not_compute_release_targets(self) -> None:
        repo = mock.Mock()
        repo.owner = SimpleNamespace(login="Telepact")
        repo.get_pulls.return_value = iter(())
        repo.create_pull.return_value = SimpleNamespace(html_url="https://github.com/Telepact/telepact/pull/99")

        github_client = mock.Mock()
        github_client.get_repo.return_value = repo

        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            (repo_root / "VERSION.txt").write_text("1.0.0-alpha.214", encoding="utf-8")
            with _pushd(repo_root):
                with (
                    mock.patch("telepact_project_cli.commands.repository_automation.Github", return_value=github_client),
                    mock.patch("telepact_project_cli.commands.repository_automation.compute_release_manifest_from_git") as compute_release_manifest_from_git,
                    mock.patch("telepact_project_cli.commands.repository_automation._git") as git,
                    mock.patch("telepact_project_cli.commands.repository_automation._push_current_branch") as push_current_branch,
                    mock.patch(
                        "telepact_project_cli.commands.repository_automation.create_version_bump_commit",
                        return_value="1.0.0-alpha.215",
                    ) as create_version_bump_commit,
                ):
                    result = runner.invoke(
                        main,
                        ["open-version-bump-pr"],
                        env={
                            "GITHUB_TOKEN": "token",
                            "GITHUB_REPOSITORY": "Telepact/telepact",
                        },
                    )

        self.assertEqual(result.exit_code, 0, msg=result.output)
        compute_release_manifest_from_git.assert_not_called()
        git.assert_called_once_with("checkout", "-B", "version-bump/1.0.0-alpha.215")
        create_version_bump_commit.assert_called_once_with(compute_release_targets=False)
        push_current_branch.assert_called_once_with("version-bump/1.0.0-alpha.215")
        repo.create_pull.assert_called_once_with(
            title="Bump version to 1.0.0-alpha.215",
            body="Automated version bump PR.",
            head="Telepact:version-bump/1.0.0-alpha.215",
            base="main",
        )
        created_pr = repo.create_pull.return_value
        created_pr.enable_automerge.assert_called_once_with(merge_method="SQUASH")

    def test_process_merge_ready_pull_request_admin_flow_updates_and_merges(self) -> None:
        initial_pr = mock.Mock()
        initial_pr.number = 7
        initial_pr.state = "open"
        initial_pr.head = SimpleNamespace(sha="head-1", ref="feature")
        initial_pr.mark_ready_for_review = mock.Mock()
        initial_pr.draft = True
        ready_pr = mock.Mock()
        ready_pr.number = 7
        ready_pr.state = "open"
        ready_pr.head = SimpleNamespace(sha="head-1", ref="feature")
        ready_pr.mergeable_state = "behind"
        ready_pr.update_branch = mock.Mock()

        updated_pr = mock.Mock()
        updated_pr.number = 7
        updated_pr.state = "open"
        updated_pr.head = SimpleNamespace(sha="head-2", ref="feature")
        updated_pr.merge.return_value = SimpleNamespace(merged=True, message="")

        issue = mock.Mock()
        issue.get_comments.return_value = [
            SimpleNamespace(body="not this", user=SimpleNamespace(login="other-user")),
            SimpleNamespace(body="/merge", user=SimpleNamespace(login="admin-user")),
        ]

        repo = mock.Mock()
        repo.has_in_collaborators.return_value = True
        repo.get_collaborator_permission.return_value = "admin"
        repo.get_issue.return_value = issue
        repo.get_pull.return_value = initial_pr

        validate_merge_request = mock.Mock()
        with (
            mock.patch(
                "telepact_project_cli.commands.repository_automation._wait_for_pr_stable",
                side_effect=[initial_pr, ready_pr],
            ),
            mock.patch(
                "telepact_project_cli.commands.repository_automation._wait_for_pr_head_update",
                return_value=updated_pr,
            ),
            mock.patch(
                "telepact_project_cli.commands.repository_automation._validate_merge_request",
                validate_merge_request,
            ),
            mock.patch("telepact_project_cli.commands.repository_automation._remove_merge_ready_label") as remove_merge_ready_label,
            mock.patch("telepact_project_cli.commands.repository_automation._verify_pull_request_ci"),
        ):
            _process_merge_ready_pull_request(repo, 7)

        initial_pr.mark_ready_for_review.assert_called_once_with()
        ready_pr.update_branch.assert_called_once_with(expected_head_sha="head-1")
        self.assertEqual(validate_merge_request.call_count, 1)
        updated_pr.merge.assert_called_once_with(merge_method="squash", sha="head-2")
        remove_merge_ready_label.assert_called_once_with(repo, 7)

    def test_process_merge_ready_pull_request_removes_label_from_closed_pr_without_waiting(self) -> None:
        closed_pr = mock.Mock()
        closed_pr.number = 7
        closed_pr.state = "closed"

        issue = mock.Mock()
        issue.get_comments.return_value = [
            SimpleNamespace(body="/merge", user=SimpleNamespace(login="admin-user")),
        ]

        repo = mock.Mock()
        repo.has_in_collaborators.return_value = True
        repo.get_collaborator_permission.return_value = "admin"
        repo.get_issue.return_value = issue
        repo.get_pull.return_value = closed_pr

        with (
            mock.patch("telepact_project_cli.commands.repository_automation._remove_merge_ready_label") as remove_merge_ready_label,
            mock.patch("telepact_project_cli.commands.repository_automation._wait_for_pr_stable") as wait_for_pr_stable,
            mock.patch("telepact_project_cli.commands.repository_automation._validate_merge_request") as validate_merge_request,
        ):
            _process_merge_ready_pull_request(repo, 7)

        remove_merge_ready_label.assert_called_once_with(repo, 7)
        wait_for_pr_stable.assert_not_called()
        validate_merge_request.assert_not_called()

    def test_merge_pr_command_removes_label_and_continues_after_failure(self) -> None:
        repo = mock.Mock()
        github_client = mock.Mock()
        github_client.get_repo.return_value = repo

        runner = CliRunner()
        with (
            mock.patch("telepact_project_cli.commands.repository_automation.Github", return_value=github_client),
            mock.patch(
                "telepact_project_cli.commands.repository_automation._next_merge_ready_pr_number",
                side_effect=[7, 8, None],
            ),
            mock.patch(
                "telepact_project_cli.commands.repository_automation._process_merge_ready_pull_request",
                side_effect=[RuntimeError("boom"), None],
            ) as process_merge_ready_pull_request,
            mock.patch("telepact_project_cli.commands.repository_automation._remove_merge_ready_label") as remove_merge_ready_label,
        ):
            result = runner.invoke(
                main,
                ["merge-pr"],
                env={
                    "GITHUB_TOKEN": "token",
                    "GITHUB_REPOSITORY": "Telepact/telepact",
                },
            )

        self.assertNotEqual(result.exit_code, 0)
        process_merge_ready_pull_request.assert_has_calls([mock.call(repo, 7), mock.call(repo, 8)])
        remove_merge_ready_label.assert_called_once_with(repo, 7)
        self.assertEqual(str(result.exception), "Merge loop completed with failures: #7: RuntimeError('boom')")

    def test_merge_pr_command_exits_cleanly_when_no_merge_ready_prs_exist(self) -> None:
        repo = mock.Mock()
        github_client = mock.Mock()
        github_client.get_repo.return_value = repo

        runner = CliRunner()
        with (
            mock.patch("telepact_project_cli.commands.repository_automation.Github", return_value=github_client),
            mock.patch(
                "telepact_project_cli.commands.repository_automation._next_merge_ready_pr_number",
                return_value=None,
            ),
        ):
            result = runner.invoke(
                main,
                ["merge-pr"],
                env={
                    "GITHUB_TOKEN": "token",
                    "GITHUB_REPOSITORY": "Telepact/telepact",
                },
            )

        self.assertEqual(result.exit_code, 0, msg=result.output)
        self.assertIn("No merge-ready pull requests remain.", result.output)


if __name__ == "__main__":
    unittest.main()
