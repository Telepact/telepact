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
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_ROOT))

from click.testing import CliRunner

from telepact_project_cli.cli import main
from telepact_project_cli.commands.repository_automation import _approval_count, _should_create_approval_review, _summarize_failed_statuses


class RepositoryAutomationTests(unittest.TestCase):
    def test_approval_count_uses_latest_state_per_reviewer(self) -> None:
        pr = SimpleNamespace(
            get_reviews=lambda: [
                SimpleNamespace(user=SimpleNamespace(login="alice"), state="APPROVED"),
                SimpleNamespace(user=SimpleNamespace(login="bob"), state="APPROVED"),
                SimpleNamespace(user=SimpleNamespace(login="alice"), state="CHANGES_REQUESTED"),
                SimpleNamespace(user=SimpleNamespace(login="carol"), state="COMMENTED"),
            ]
        )

        self.assertEqual(_approval_count(pr), 1)

    def test_summarize_failed_statuses_returns_only_failed_contexts(self) -> None:
        commit = SimpleNamespace(
            get_combined_status=lambda: SimpleNamespace(
                state="failure",
                statuses=[
                    SimpleNamespace(context="lint", state="success"),
                    SimpleNamespace(context="unit", state="failure"),
                    SimpleNamespace(context="queue", state="pending"),
                    SimpleNamespace(context="release", state="error"),
                ]
            )
        )

        failed = _summarize_failed_statuses(commit)

        self.assertEqual(failed, ["unit=failure", "release=error"])

    def test_should_create_approval_review_rejects_blocked_non_admin(self) -> None:
        pr = SimpleNamespace(number=7, mergeable_state="blocked")

        with self.assertRaisesRegex(RuntimeError, "waiting on required code review"):
            _should_create_approval_review(pr, is_admin=False)

    def test_should_create_approval_review_allows_blocked_admin_without_approval(self) -> None:
        pr = SimpleNamespace(number=7, mergeable_state="blocked")

        self.assertFalse(_should_create_approval_review(pr, is_admin=True))

    def test_merge_pr_command_rejects_non_collaborator(self) -> None:
        repo = mock.Mock()
        repo.has_in_collaborators.return_value = False

        github_client = mock.Mock()
        github_client.get_repo.return_value = repo

        runner = CliRunner()
        with mock.patch("telepact_project_cli.commands.repository_automation.Github", return_value=github_client):
            result = runner.invoke(
                main,
                ["merge-pr"],
                env={
                    "GITHUB_TOKEN": "token",
                    "GITHUB_REPOSITORY": "Telepact/telepact",
                    "COMMENTER_LOGIN": "outsider",
                    "PR_NUMBER": "7",
                },
            )

        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("not a repository collaborator", result.output)

    def test_merge_pr_command_admin_bypasses_blocked_state_without_approval(self) -> None:
        initial_pr = mock.Mock()
        initial_pr.number = 7
        initial_pr.head = SimpleNamespace(sha="head-1", ref="feature")
        initial_pr.mark_ready_for_review = mock.Mock()
        initial_pr.draft = True

        ready_pr = mock.Mock()
        ready_pr.number = 7
        ready_pr.head = SimpleNamespace(sha="head-1", ref="feature")
        ready_pr.mergeable_state = "behind"
        ready_pr.update_branch = mock.Mock()

        updated_pr = mock.Mock()
        updated_pr.number = 7
        updated_pr.head = SimpleNamespace(sha="head-2", ref="feature")

        bumped_pr = mock.Mock()
        bumped_pr.number = 7
        bumped_pr.head = SimpleNamespace(sha="head-3", ref="feature")
        bumped_pr.mergeable_state = "blocked"
        bumped_pr.create_review = mock.Mock()
        bumped_pr.merge.return_value = SimpleNamespace(merged=True, message="")

        repo = mock.Mock()
        repo.has_in_collaborators.return_value = True
        repo.get_collaborator_permission.return_value = "admin"
        repo.get_pull.return_value = initial_pr

        github_client = mock.Mock()
        github_client.get_repo.return_value = repo

        runner = CliRunner()
        with (
            mock.patch("telepact_project_cli.commands.repository_automation.Github", return_value=github_client),
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
            mock.patch("telepact_project_cli.commands.repository_automation._validate_merge_request"),
            mock.patch("telepact_project_cli.commands.repository_automation._verify_pr_ci_status"),
            mock.patch("telepact_project_cli.commands.repository_automation._checkout_pr_branch"),
            mock.patch("telepact_project_cli.commands.repository_automation._push_current_branch"),
            mock.patch("telepact_project_cli.commands.repository_automation._current_head_sha", return_value="head-3"),
            mock.patch("telepact_project_cli.commands.repository_automation.create_version_bump_commit"),
        ):
            result = runner.invoke(
                main,
                ["merge-pr"],
                env={
                    "GITHUB_TOKEN": "token",
                    "GITHUB_REPOSITORY": "Telepact/telepact",
                    "COMMENTER_LOGIN": "admin-user",
                    "PR_NUMBER": "7",
                },
            )

        self.assertEqual(result.exit_code, 0, msg=result.output)
        initial_pr.mark_ready_for_review.assert_called_once_with()
        ready_pr.update_branch.assert_called_once_with(expected_head_sha="head-1")
        bumped_pr.create_review.assert_not_called()
        bumped_pr.merge.assert_called_once_with(merge_method="squash", sha="head-3")


if __name__ == "__main__":
    unittest.main()
