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
import subprocess
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from click.testing import CliRunner

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_ROOT))

from telepact_project_cli.cli import main
from telepact_project_cli.commands import repository_automation


class RepositoryAutomationTests(unittest.TestCase):
    def test_validate_merge_commenter_rejects_insufficient_permission(self) -> None:
        repo = mock.Mock()
        repo.has_in_collaborators.return_value = True
        repo.get_collaborator_permission.return_value = "read"

        with self.assertRaisesRegex(Exception, "cannot merge pull requests"):
            repository_automation._validate_merge_commenter(repo, "octocat")

    def test_wait_for_pull_request_requirements_fails_when_head_changes_while_waiting(self) -> None:
        branch = SimpleNamespace(protected=False)
        first_pr = SimpleNamespace(
            number=7,
            state="open",
            draft=False,
            base=SimpleNamespace(ref="main"),
            head=SimpleNamespace(sha="sha-1", repo=SimpleNamespace(full_name="Telepact/telepact")),
            mergeable=None,
            mergeable_state="unknown",
        )
        second_pr = SimpleNamespace(
            number=7,
            state="open",
            draft=False,
            base=SimpleNamespace(ref="main"),
            head=SimpleNamespace(sha="sha-2", repo=SimpleNamespace(full_name="Telepact/telepact")),
            mergeable=True,
            mergeable_state="clean",
            get_reviews=lambda: [],
        )
        repo = mock.Mock()
        repo.full_name = "Telepact/telepact"
        repo.get_branch.return_value = branch
        repo.get_pull.side_effect = [first_pr, second_pr]

        with (
            mock.patch("telepact_project_cli.commands.repository_automation.time.sleep"),
            self.assertRaisesRegex(Exception, "head changed to sha-2"),
        ):
            repository_automation._wait_for_pull_request_requirements(repo, 7, "sha-1")

    def test_merge_pr_command_merges_after_bump_and_recheck(self) -> None:
        pr = mock.Mock()
        pr.number = 7
        pr.head = SimpleNamespace(ref="feature/test", sha="sha-before")
        pr.get_files.return_value = [
            SimpleNamespace(filename="sdk/cli/pyproject.toml"),
            SimpleNamespace(filename="lib/py/pyproject.toml"),
        ]
        pr.merge.return_value = SimpleNamespace(merged=True, message="merged")

        repo = mock.Mock()
        repo.get_pull.return_value = pr

        github_client = mock.Mock()
        github_client.get_repo.return_value = repo

        run_git_calls: list[tuple[tuple[object, ...], dict[str, object]]] = []

        def run_git_side_effect(*args, **kwargs):
            run_git_calls.append((args, kwargs))
            if args == ("rev-parse", "HEAD"):
                return subprocess.CompletedProcess(["git", "rev-parse", "HEAD"], 0, stdout="sha-after\n")
            return subprocess.CompletedProcess(["git", *map(str, args)], 0, stdout="")

        runner = CliRunner()
        with (
            mock.patch("telepact_project_cli.commands.repository_automation.Github", return_value=github_client),
            mock.patch("telepact_project_cli.commands.repository_automation._validate_merge_commenter"),
            mock.patch(
                "telepact_project_cli.commands.repository_automation._tidy_pull_request",
                return_value=(pr, "sha-original"),
            ),
            mock.patch("telepact_project_cli.commands.repository_automation._wait_for_pull_request_requirements") as wait_mock,
            mock.patch("telepact_project_cli.commands.repository_automation._configure_git_identity"),
            mock.patch("telepact_project_cli.commands.repository_automation.bump_version") as bump_mock,
            mock.patch("telepact_project_cli.commands.repository_automation._wait_for_head_sha") as wait_for_head_mock,
            mock.patch("telepact_project_cli.commands.repository_automation._run_git", side_effect=run_git_side_effect),
        ):
            result = runner.invoke(
                main,
                ["merge-pr"],
                env={
                    "PR_NUMBER": "7",
                    "MERGE_COMMENTER": "octocat",
                    "GITHUB_TOKEN": "token",
                    "GITHUB_REPOSITORY": "Telepact/telepact",
                },
            )

        self.assertEqual(result.exit_code, 0, msg=result.output)
        self.assertEqual(wait_mock.call_args_list, [mock.call(repo, 7, "sha-before"), mock.call(repo, 7, "sha-after")])
        bump_mock.assert_called_once_with(
            changed_paths=["lib/py/pyproject.toml", "sdk/cli/pyproject.toml"],
            pr_number=7,
            commit_changes=True,
        )
        wait_for_head_mock.assert_called_once_with(repo, 7, "sha-after", previous_head_sha="sha-before")
        pr.merge.assert_called_once_with(merge_method="squash", sha="sha-after")
        self.assertIn((("push", "origin", "HEAD:refs/heads/feature/test"), {}), run_git_calls)


if __name__ == "__main__":
    unittest.main()
