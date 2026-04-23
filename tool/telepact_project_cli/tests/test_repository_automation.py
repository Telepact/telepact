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
from types import SimpleNamespace
from unittest import mock

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_ROOT))

from click.testing import CliRunner

from telepact_project_cli.cli import main
from telepact_project_cli.commands.repository_automation import (
    _combined_status_state,
    _process_merge_ready_pull_request,
    _pull_request_ci_state,
    _validate_merge_request,
    _verify_pull_request_ci,
    _wait_for_pr_stable,
)


class RepositoryAutomationTests(unittest.TestCase):
    def test_should_release_command_returns_true_when_head_commit_changes_version_file(self) -> None:
        runner = CliRunner()
        with mock.patch(
            "telepact_project_cli.commands.repository_automation.subprocess.run",
            return_value=SimpleNamespace(stdout="VERSION.txt\nsdk/cli/pyproject.toml\n"),
        ) as subprocess_run:
            result = runner.invoke(main, ["should-release"])

        self.assertEqual(result.exit_code, 0, msg=result.output)
        self.assertEqual(result.output, "true\n")
        subprocess_run.assert_called_once_with(
            ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", "--root", "HEAD"],
            check=True,
            text=True,
            stdout=mock.ANY,
            stderr=mock.ANY,
        )

    def test_should_release_command_returns_false_when_head_commit_does_not_change_version_file(self) -> None:
        runner = CliRunner()
        with mock.patch(
            "telepact_project_cli.commands.repository_automation.subprocess.run",
            return_value=SimpleNamespace(stdout="README.md\n"),
        ):
            result = runner.invoke(main, ["should-release"])

        self.assertEqual(result.exit_code, 0, msg=result.output)
        self.assertEqual(result.output, "false\n")

    def test_should_release_command_calls_write_github_outputs_when_version_file_not_changed(self) -> None:
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmp_dir:
            github_output = Path(tmp_dir) / "github-output.txt"
            with (
                mock.patch(
                    "telepact_project_cli.commands.repository_automation.subprocess.run",
                    return_value=SimpleNamespace(stdout="README.md\n"),
                ),
                mock.patch(
                    "telepact_project_cli.commands.repository_automation._write_github_outputs",
                ) as write_github_outputs,
            ):
                result = runner.invoke(
                    main,
                    ["should-release", "--github-output", str(github_output)],
                )

        self.assertEqual(result.exit_code, 0, msg=result.output)
        write_github_outputs.assert_called_once_with(github_output, {"should_release": False})

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

    def test_process_merge_ready_pull_request_admin_flow_updates_and_merges(self) -> None:
        initial_pr = mock.Mock()
        initial_pr.number = 7
        initial_pr.state = "open"
        initial_pr.head = SimpleNamespace(sha="head-1", ref="feature")
        initial_pr.mark_ready_for_review = mock.Mock()
        initial_pr.draft = True
        initial_pr.get_files.return_value = [
            SimpleNamespace(filename="lib/py/pyproject.toml"),
            SimpleNamespace(filename="sdk/cli/pyproject.toml"),
        ]

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

        bumped_pr = mock.Mock()
        bumped_pr.number = 7
        bumped_pr.state = "open"
        bumped_pr.head = SimpleNamespace(sha="head-3", ref="feature")
        bumped_pr.merge.return_value = SimpleNamespace(merged=True, message="")

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
                side_effect=[initial_pr, ready_pr, bumped_pr],
            ),
            mock.patch(
                "telepact_project_cli.commands.repository_automation._wait_for_pr_head_update",
                return_value=updated_pr,
            ),
            mock.patch(
                "telepact_project_cli.commands.repository_automation._wait_for_expected_head",
                return_value=bumped_pr,
            ),
            mock.patch(
                "telepact_project_cli.commands.repository_automation._validate_merge_request",
                validate_merge_request,
            ),
            mock.patch("telepact_project_cli.commands.repository_automation._remove_merge_ready_label") as remove_merge_ready_label,
            mock.patch("telepact_project_cli.commands.repository_automation._verify_pull_request_ci"),
            mock.patch("telepact_project_cli.commands.repository_automation._checkout_pr_branch"),
            mock.patch("telepact_project_cli.commands.repository_automation._push_current_branch"),
            mock.patch("telepact_project_cli.commands.repository_automation._current_head_sha", return_value="head-3"),
            mock.patch("telepact_project_cli.commands.repository_automation.create_version_bump_commit") as create_version_bump_commit,
        ):
            _process_merge_ready_pull_request(repo, 7)

        initial_pr.mark_ready_for_review.assert_called_once_with()
        ready_pr.update_branch.assert_called_once_with(expected_head_sha="head-1")
        self.assertEqual(validate_merge_request.call_count, 1)
        create_version_bump_commit.assert_called_once_with(
            7,
            changed_paths=["lib/py/pyproject.toml", "sdk/cli/pyproject.toml"],
        )
        bumped_pr.merge.assert_called_once_with(merge_method="squash", sha="head-3")
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
