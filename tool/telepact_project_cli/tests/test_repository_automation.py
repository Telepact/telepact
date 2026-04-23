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
from telepact_project_cli.commands.repository_automation import (
    MERGE_READY_LABEL,
    _combined_status_state,
    _list_open_merge_ready_pull_requests,
    _pull_request_ci_state,
    _validate_merge_request,
    _verify_pull_request_ci,
)


class RepositoryAutomationTests(unittest.TestCase):
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

    def test_list_open_merge_ready_pull_requests_filters_and_orders(self) -> None:
        repo = mock.Mock()
        repo.get_pulls.return_value = [
            SimpleNamespace(number=3, get_labels=lambda: [SimpleNamespace(name=MERGE_READY_LABEL)]),
            SimpleNamespace(number=4, get_labels=lambda: [SimpleNamespace(name="bug")]),
            SimpleNamespace(number=5, get_labels=lambda: [SimpleNamespace(name=MERGE_READY_LABEL)]),
        ]

        pull_requests = _list_open_merge_ready_pull_requests(repo)

        self.assertEqual([pr.number for pr in pull_requests], [3, 5])
        repo.get_pulls.assert_called_once_with(state="open", sort="created", direction="asc", base="main")

    def test_mark_pr_merge_ready_command_rejects_non_collaborator(self) -> None:
        repo = mock.Mock()
        repo.has_in_collaborators.return_value = False

        github_client = mock.Mock()
        github_client.get_repo.return_value = repo

        runner = CliRunner()
        with mock.patch("telepact_project_cli.commands.repository_automation.Github", return_value=github_client):
            result = runner.invoke(
                main,
                ["mark-pr-merge-ready"],
                env={
                    "GITHUB_TOKEN": "token",
                    "GITHUB_REPOSITORY": "Telepact/telepact",
                    "COMMENTER_LOGIN": "outsider",
                    "PR_NUMBER": "7",
                },
            )

        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("not a repository collaborator", result.output)

    def test_mark_pr_merge_ready_command_labels_pull_request_and_sets_skip_output(self) -> None:
        pr = mock.Mock()
        pr.number = 7
        pr.state = "open"
        pr.get_labels.return_value = []

        queued_pr = SimpleNamespace(number=7, get_labels=lambda: [SimpleNamespace(name=MERGE_READY_LABEL)])
        other_pr = SimpleNamespace(number=8, get_labels=lambda: [SimpleNamespace(name=MERGE_READY_LABEL)])

        repo = mock.Mock()
        repo.has_in_collaborators.return_value = True
        repo.get_collaborator_permission.return_value = "write"
        repo.get_pull.return_value = pr
        repo.get_pulls.return_value = [queued_pr, other_pr]

        github_client = mock.Mock()
        github_client.get_repo.return_value = repo

        runner = CliRunner()
        with runner.isolated_filesystem():
            output_path = Path("github-output.txt")
            with mock.patch("telepact_project_cli.commands.repository_automation.Github", return_value=github_client):
                result = runner.invoke(
                    main,
                    ["mark-pr-merge-ready"],
                    env={
                        "GITHUB_TOKEN": "token",
                        "GITHUB_REPOSITORY": "Telepact/telepact",
                        "COMMENTER_LOGIN": "maintainer",
                        "PR_NUMBER": "7",
                        "GITHUB_OUTPUT": str(output_path),
                    },
                )

            self.assertEqual(result.exit_code, 0, msg=result.output)
            pr.add_to_labels.assert_called_once_with(MERGE_READY_LABEL)
            self.assertIn(f"skip_merge_loop=true\n", output_path.read_text())
            self.assertIn(f"merge_ready_count=2\n", output_path.read_text())

    def test_merge_pr_command_processes_all_merge_ready_pull_requests(self) -> None:
        first_pr = SimpleNamespace(number=7, get_labels=lambda: [SimpleNamespace(name=MERGE_READY_LABEL)])
        second_pr = SimpleNamespace(number=8, get_labels=lambda: [SimpleNamespace(name=MERGE_READY_LABEL)])

        repo = mock.Mock()
        repo.get_pulls.side_effect = [
            [first_pr, second_pr],
            [second_pr],
            [],
        ]

        github_client = mock.Mock()
        github_client.get_repo.return_value = repo

        runner = CliRunner()
        with (
            mock.patch("telepact_project_cli.commands.repository_automation.Github", return_value=github_client),
            mock.patch("telepact_project_cli.commands.repository_automation._process_merge_pull_request") as process_merge_pull_request,
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
        self.assertEqual(process_merge_pull_request.call_count, 2)
        self.assertEqual(process_merge_pull_request.call_args_list[0], mock.call(repo, 7, is_admin=False))
        self.assertEqual(process_merge_pull_request.call_args_list[1], mock.call(repo, 8, is_admin=False))

    def test_merge_pr_processing_flow_updates_approves_and_merges(self) -> None:
        initial_pr = mock.Mock()
        initial_pr.number = 7
        initial_pr.head = SimpleNamespace(sha="head-1", ref="feature")
        initial_pr.mark_ready_for_review = mock.Mock()
        initial_pr.draft = True
        initial_pr.get_files.return_value = [
            SimpleNamespace(filename="lib/py/pyproject.toml"),
            SimpleNamespace(filename="sdk/cli/pyproject.toml"),
        ]

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
        bumped_pr.merge.return_value = SimpleNamespace(merged=True, message="")

        repo = mock.Mock()
        repo.has_in_collaborators.return_value = True
        repo.get_collaborator_permission.return_value = "admin"
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
            mock.patch("telepact_project_cli.commands.repository_automation._verify_pull_request_ci"),
            mock.patch("telepact_project_cli.commands.repository_automation._checkout_pr_branch"),
            mock.patch("telepact_project_cli.commands.repository_automation._push_current_branch"),
            mock.patch("telepact_project_cli.commands.repository_automation._current_head_sha", return_value="head-3"),
            mock.patch("telepact_project_cli.commands.repository_automation.create_version_bump_commit") as create_version_bump_commit,
        ):
            from telepact_project_cli.commands.repository_automation import _process_merge_pull_request

            _process_merge_pull_request(repo, 7, is_admin=True)

        initial_pr.mark_ready_for_review.assert_called_once_with()
        ready_pr.update_branch.assert_called_once_with(expected_head_sha="head-1")
        self.assertEqual(validate_merge_request.call_count, 2)
        create_version_bump_commit.assert_called_once_with(
            7,
            changed_paths=["lib/py/pyproject.toml", "sdk/cli/pyproject.toml"],
        )
        bumped_pr.merge.assert_called_once_with(merge_method="squash", sha="head-3")


if __name__ == "__main__":
    unittest.main()
