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

from click.testing import CliRunner

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_ROOT))

from telepact_project_cli.cli import main
from telepact_project_cli.commands.repository_automation import _wait_for_pr_requirements


class RepositoryAutomationTests(unittest.TestCase):
    def test_wait_for_pr_requirements_fails_if_head_changes_while_waiting(self) -> None:
        repo = mock.Mock()
        repo.full_name = "Telepact/telepact"
        repo.get_branch.return_value = mock.Mock(
            get_required_status_checks=mock.Mock(return_value=SimpleNamespace(contexts=["Build"]))
        )

        commit = mock.Mock()
        commit.get_statuses.return_value = []
        commit.get_check_runs.return_value = [
            SimpleNamespace(name="Build", status="in_progress", conclusion=None)
        ]
        repo.get_commit.return_value = commit

        repo.get_pull.side_effect = [
            SimpleNamespace(
                number=9,
                state="open",
                base=SimpleNamespace(ref="main"),
                head=SimpleNamespace(
                    sha="abc123",
                    repo=SimpleNamespace(full_name="Telepact/telepact"),
                ),
                draft=False,
                mergeable=None,
                mergeable_state="unknown",
            ),
            SimpleNamespace(
                number=9,
                state="open",
                base=SimpleNamespace(ref="main"),
                head=SimpleNamespace(
                    sha="def456",
                    repo=SimpleNamespace(full_name="Telepact/telepact"),
                ),
                draft=False,
                mergeable=None,
                mergeable_state="unknown",
            ),
        ]

        with (
            mock.patch("telepact_project_cli.commands.repository_automation.time.sleep"),
            self.assertRaisesRegex(Exception, "received new commits"),
        ):
            _wait_for_pr_requirements(repo, 9, "abc123")

    def test_merge_pr_command_rejects_ineligible_commenter(self) -> None:
        repo = mock.Mock()
        repo.get_collaborator_permission.return_value = "read"
        repo.get_pull.return_value = SimpleNamespace(
            number=9,
            state="open",
            base=SimpleNamespace(ref="main"),
            head=SimpleNamespace(
                sha="abc123",
                repo=SimpleNamespace(full_name="Telepact/telepact"),
            ),
        )

        github_client = mock.Mock(get_repo=mock.Mock(return_value=repo))
        runner = CliRunner()

        with mock.patch("telepact_project_cli.commands.repository_automation.Github", return_value=github_client):
            result = runner.invoke(
                main,
                ["merge-pr"],
                env={
                    "COMMENTER_LOGIN": "reader",
                    "GITHUB_REPOSITORY": "Telepact/telepact",
                    "GITHUB_TOKEN": "token",
                    "PR_NUMBER": "9",
                },
            )

        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("does not have merge permission", result.output)

    def test_merge_pr_command_merges_after_validation_and_version_bump(self) -> None:
        initial_pr = SimpleNamespace(
            number=9,
            state="open",
            base=SimpleNamespace(ref="main"),
            head=SimpleNamespace(
                sha="abc123",
                ref="feature/test",
                repo=SimpleNamespace(full_name="Telepact/telepact"),
            ),
            draft=False,
        )
        final_pr = mock.Mock()
        final_pr.head.sha = "def456"
        final_pr.merge.return_value = SimpleNamespace(merged=True, message="merged")

        repo = mock.Mock()
        repo.full_name = "Telepact/telepact"
        repo.get_collaborator_permission.return_value = "write"
        repo.get_pull.return_value = initial_pr

        github_client = mock.Mock(get_repo=mock.Mock(return_value=repo))
        runner = CliRunner()

        with (
            mock.patch("telepact_project_cli.commands.repository_automation.Github", return_value=github_client),
            mock.patch("telepact_project_cli.commands.repository_automation._checkout_pr_branch", return_value="feature/test"),
            mock.patch("telepact_project_cli.commands.repository_automation._tidy_up_pull_request", return_value=initial_pr),
            mock.patch(
                "telepact_project_cli.commands.repository_automation._wait_for_pr_requirements",
                side_effect=[initial_pr, final_pr],
            ),
            mock.patch(
                "telepact_project_cli.commands.repository_automation._wait_for_head_sha",
                return_value=final_pr,
            ),
            mock.patch(
                "telepact_project_cli.commands.repository_automation._list_changed_paths_against_main",
                return_value=["sdk/cli/pyproject.toml"],
            ),
            mock.patch("telepact_project_cli.commands.repository_automation.bump_version"),
            mock.patch(
                "telepact_project_cli.commands.repository_automation._run_git",
                side_effect=lambda args, capture_output=False: "def456" if args == ["rev-parse", "HEAD"] else "",
            ) as run_git,
        ):
            result = runner.invoke(
                main,
                ["merge-pr"],
                env={
                    "COMMENTER_LOGIN": "writer",
                    "GITHUB_REPOSITORY": "Telepact/telepact",
                    "GITHUB_TOKEN": "token",
                    "PR_NUMBER": "9",
                },
            )

        self.assertEqual(result.exit_code, 0, msg=result.output)
        run_git.assert_any_call(["push", "origin", "HEAD:feature/test"])
        final_pr.merge.assert_called_once_with(merge_method="squash", sha="def456")


if __name__ == "__main__":
    unittest.main()
