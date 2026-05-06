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

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import click
import yaml

RELEASE_CONFIG_RELATIVE_PATH = Path(".release/release-targets.yaml")
VERSION_FILE_RELATIVE_PATH = Path("VERSION.txt")
# Use ASCII Unit Separator (`\x1f`, rendered in git log format strings as `%x1f`)
# so git log records can be split safely even when commit subjects contain common
# delimiters like pipes, commas, or colons.
GIT_LOG_FIELD_SEPARATOR = "\x1f"
GIT_LOG_FORMAT = "--format=%H%x1f%s"

PUBLISH_TARGETS = ("java", "ts", "py", "go", "cli", "console", "prettier")


@dataclass(frozen=True)
class ReleaseProjectRule:
    name: str
    paths: tuple[str, ...]
    is_dependency_for: tuple[str, ...]


@dataclass(frozen=True)
class ReleaseTargetConfig:
    projects: dict[str, ReleaseProjectRule]
    force_all_if_changed: tuple[str, ...]


@dataclass(frozen=True)
class ReleaseComparison:
    """Exact commits used for release-target comparison.

    base_commit is None when the comparison has no explicit git base commit, such as
    the initial release snapshot where the manifest is derived from the tree at head_commit.
    """

    base_commit: str | None
    head_commit: str

    def to_dict(self) -> dict[str, str | None]:
        return {
            "base_commit": self.base_commit,
            "head_commit": self.head_commit,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ReleaseComparison":
        if not isinstance(data, dict):
            raise click.ClickException("Release manifest field 'comparison' must be a JSON object.")
        base_commit = data.get("base_commit")
        if base_commit is not None and not isinstance(base_commit, str):
            raise click.ClickException("Release manifest comparison field 'base_commit' must be a string or null.")
        head_commit = data.get("head_commit")
        if not isinstance(head_commit, str):
            raise click.ClickException("Release manifest comparison field 'head_commit' must be a string.")
        if not head_commit:
            raise click.ClickException("Release manifest comparison field 'head_commit' must be a non-empty string.")
        return cls(base_commit=base_commit, head_commit=head_commit)


@dataclass(frozen=True)
class ReleaseManifest:
    version: str
    pr_number: int | None
    comparison: ReleaseComparison
    changed_paths: tuple[str, ...]
    direct_targets: tuple[str, ...]
    targets: tuple[str, ...]

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "pr_number": self.pr_number,
            "comparison": self.comparison.to_dict(),
            "changed_paths": list(self.changed_paths),
            "direct_targets": list(self.direct_targets),
            "targets": list(self.targets),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ReleaseManifest":
        if not isinstance(data, dict):
            raise click.ClickException("Release manifest must be a JSON object.")
        version = data.get("version")
        if not isinstance(version, str) or not version:
            raise click.ClickException("Release manifest must define a non-empty string 'version'.")
        pr_number = data.get("pr_number")
        if pr_number is not None and not isinstance(pr_number, int):
            raise click.ClickException("Release manifest field 'pr_number' must be an integer or null.")

        def _string_list(field_name: str) -> tuple[str, ...]:
            value = data.get(field_name)
            if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
                raise click.ClickException(f"Release manifest field {field_name!r} must be a string list.")
            return tuple(value)
        if "comparison" not in data:
            raise click.ClickException("Release manifest must define a 'comparison' object.")

        return cls(
            version=version,
            pr_number=pr_number,
            comparison=ReleaseComparison.from_dict(data["comparison"]),
            changed_paths=_string_list("changed_paths"),
            direct_targets=_string_list("direct_targets"),
            targets=_string_list("targets"),
        )


@dataclass(frozen=True)
class ReleaseCommit:
    sha: str
    subject: str


def find_repo_root(start: Path | str = ".") -> Path:
    start_path = Path(start).resolve()
    for candidate in [start_path, *start_path.parents]:
        if (candidate / "VERSION.txt").exists():
            return candidate
    raise click.ClickException("Unable to locate repo root (VERSION.txt not found).")


def _normalize_repo_path(path: str) -> str:
    normalized = path.strip().strip("/")
    return normalized.replace("\\", "/")


def _git_stdout(repo_root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return result.stdout


def _version_change_commits(repo_root: Path, ref: str = "HEAD") -> list[str]:
    try:
        stdout = _git_stdout(repo_root, "log", "--format=%H", ref, "--", VERSION_FILE_RELATIVE_PATH.as_posix())
    except subprocess.CalledProcessError as exc:
        raise click.ClickException(f"Unable to inspect {VERSION_FILE_RELATIVE_PATH} history at {ref}: {exc.stderr.strip()}")
    return [line.strip() for line in stdout.splitlines() if line.strip()]


def _read_version(repo_root: Path, ref: str = "HEAD") -> str:
    version_file = VERSION_FILE_RELATIVE_PATH.as_posix()
    try:
        stdout = _git_stdout(repo_root, "show", f"{ref}:{version_file}")
    except subprocess.CalledProcessError as exc:
        raise click.ClickException(f"Unable to read {version_file} at {ref}: {exc.stderr.strip()}")
    return stdout.strip()


def _previous_version_change_commit(repo_root: Path, ref: str = "HEAD") -> str | None:
    commits = _version_change_commits(repo_root, ref)
    if not commits:
        raise click.ClickException(f"No commits found that changed {VERSION_FILE_RELATIVE_PATH}.")
    if len(commits) < 2:
        return None
    return commits[1]


def _resolved_commit_sha(repo_root: Path, ref: str) -> str:
    try:
        return _git_stdout(repo_root, "rev-parse", ref).strip()
    except subprocess.CalledProcessError as exc:
        raise click.ClickException(f"Unable to resolve git ref {ref!r}: {exc.stderr.strip()}")


def _release_change_window(repo_root: Path, ref: str = "HEAD") -> tuple[str | None, str]:
    version_change_commits = _version_change_commits(repo_root, ref)
    base_commit = _previous_version_change_commit(repo_root, ref)
    end_ref = ref
    if version_change_commits and _resolved_commit_sha(repo_root, ref) == version_change_commits[0]:
        try:
            end_ref = _git_stdout(repo_root, "rev-parse", f"{ref}^").strip()
        except subprocess.CalledProcessError:
            # The initial version-setting commit has no parent; in that case diff against the commit itself.
            end_ref = ref
    return (base_commit, end_ref)


def release_comparison(repo_root: Path | str = ".", ref: str = "HEAD") -> ReleaseComparison:
    """Resolve the exact commits used for the version-window release comparison.

    base_commit is the prior VERSION.txt-changing commit when one exists. head_commit
    is the exact commit whose tree or diff is used to compute the manifest changes.
    """

    repo_root = find_repo_root(repo_root)
    base_commit, end_ref = _release_change_window(repo_root, ref)
    return ReleaseComparison(
        base_commit=base_commit,
        head_commit=_resolved_commit_sha(repo_root, end_ref),
    )


def git_ref_comparison(
    repo_root: Path | str = ".",
    *,
    base_ref: str,
    head_ref: str = "HEAD",
    use_merge_base: bool = False,
) -> ReleaseComparison:
    """Resolve the exact commits used for a ref-to-ref comparison.

    When use_merge_base is true, base_commit is the merge base of base_ref and
    head_ref. Otherwise base_commit is the resolved SHA of base_ref itself.
    """

    repo_root = find_repo_root(repo_root)
    if use_merge_base:
        try:
            base_commit = _git_stdout(repo_root, "merge-base", base_ref, head_ref).strip()
        except subprocess.CalledProcessError as exc:
            raise click.ClickException(
                f"Unable to compute merge base between {base_ref!r} and {head_ref!r}: {exc.stderr.strip()}"
            )
    else:
        base_commit = _resolved_commit_sha(repo_root, base_ref)
    return ReleaseComparison(
        base_commit=base_commit,
        head_commit=_resolved_commit_sha(repo_root, head_ref),
    )


def changed_paths_since_last_version_change(repo_root: Path | str = ".", ref: str = "HEAD") -> list[str]:
    repo_root = find_repo_root(repo_root)
    base_commit, end_ref = _release_change_window(repo_root, ref)

    try:
        if base_commit is None:
            stdout = _git_stdout(repo_root, "ls-tree", "-r", "--name-only", end_ref)
        else:
            stdout = _git_stdout(repo_root, "diff", "--name-only", f"{base_commit}..{end_ref}")
    except subprocess.CalledProcessError as exc:
        raise click.ClickException(f"Unable to compute changed paths for release planning at {ref}: {exc.stderr.strip()}")

    changed_paths = sorted(
        {
            normalized
            for path in stdout.splitlines()
            for normalized in [_normalize_repo_path(path)]
            if normalized and normalized != VERSION_FILE_RELATIVE_PATH.as_posix()
        }
    )
    return changed_paths


def commits_since_last_version_change(
    repo_root: Path | str = ".",
    ref: str = "HEAD",
    paths: Iterable[str] | None = None,
) -> tuple[ReleaseCommit, ...]:
    repo_root = find_repo_root(repo_root)
    base_commit, end_ref = _release_change_window(repo_root, ref)
    normalized_paths = tuple(
        sorted(
            {
                normalized_path
                for path in (paths or ())
                for normalized_path in [_normalize_repo_path(path)]
                if normalized_path
            }
        )
    )

    try:
        args = ["log", GIT_LOG_FORMAT, "--reverse"]
        args.append(end_ref if base_commit is None else f"{base_commit}..{end_ref}")
        if normalized_paths:
            args.extend(["--", *normalized_paths])
        stdout = _git_stdout(repo_root, *args)
    except subprocess.CalledProcessError as exc:
        raise click.ClickException(f"Unable to compute release commits at {ref}: {exc.stderr.strip()}")

    commits: list[ReleaseCommit] = []
    for line in stdout.splitlines():
        if not line.strip():
            continue
        sha, separator, subject = line.partition(GIT_LOG_FIELD_SEPARATOR)
        if not separator:
            raise click.ClickException("Unexpected git log output while computing release commits.")
        commits.append(ReleaseCommit(sha=sha.strip(), subject=subject.strip()))
    return tuple(commits)


def _load_release_target_config_data(repo_root: Path) -> dict:
    config_path = repo_root / RELEASE_CONFIG_RELATIVE_PATH
    if not config_path.exists():
        raise click.ClickException(f"Release target config not found: {config_path}")

    try:
        data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise click.ClickException(f"Invalid YAML in {config_path}: {exc}")

    if not isinstance(data, dict):
        raise click.ClickException(f"Release target config must be a mapping: {config_path}")
    return data


def load_release_target_rules(repo_root: Path | str = ".") -> ReleaseTargetConfig:
    repo_root = find_repo_root(repo_root)
    data = _load_release_target_config_data(repo_root)
    projects = data.get("projects")
    if not isinstance(projects, dict) or not projects:
        raise click.ClickException("Release target config must define a non-empty 'projects' map.")

    rules: dict[str, ReleaseProjectRule] = {}
    for name, raw_rule in projects.items():
        if not isinstance(name, str) or not name:
            raise click.ClickException("Release target names must be non-empty strings.")
        if not isinstance(raw_rule, dict):
            raise click.ClickException(f"Release target '{name}' must map to an object.")

        raw_paths = raw_rule.get("paths")
        if not isinstance(raw_paths, list) or not raw_paths or not all(isinstance(item, str) and item.strip() for item in raw_paths):
            raise click.ClickException(f"Release target '{name}' must define a non-empty string list for 'paths'.")

        raw_is_dependency_for = raw_rule.get("is_dependency_for", [])
        if not isinstance(raw_is_dependency_for, list) or not all(
            isinstance(item, str) and item.strip() for item in raw_is_dependency_for
        ):
            raise click.ClickException(
                f"Release target '{name}' must define a string list for 'is_dependency_for'."
            )

        rules[name] = ReleaseProjectRule(
            name=name,
            paths=tuple(sorted({_normalize_repo_path(item) for item in raw_paths})),
            is_dependency_for=tuple(sorted({item.strip() for item in raw_is_dependency_for})),
        )

    for name, rule in rules.items():
        for dependent_target in rule.is_dependency_for:
            if dependent_target not in rules:
                raise click.ClickException(
                    f"Release target '{name}' names unknown dependent target '{dependent_target}'."
                )

    raw_force_all_paths = data.get("force_all_if_changed", [])
    if not isinstance(raw_force_all_paths, list) or not all(
        isinstance(item, str) and item.strip() for item in raw_force_all_paths
    ):
        raise click.ClickException("Release target config 'force_all_if_changed' must be a string list.")

    return ReleaseTargetConfig(
        projects=rules,
        force_all_if_changed=tuple(sorted({_normalize_repo_path(item) for item in raw_force_all_paths})),
    )


def _matches_any_prefix(path: str, prefixes: Iterable[str]) -> bool:
    for prefix in prefixes:
        if path == prefix or path.startswith(f"{prefix}/"):
            return True
    return False


def _expand_targets(direct_targets: Iterable[str], rules: dict[str, ReleaseProjectRule]) -> list[str]:
    expanded_targets = set(direct_targets)
    queue = list(direct_targets)
    while queue:
        target = queue.pop(0)
        for dependent_target in rules[target].is_dependency_for:
            if dependent_target not in expanded_targets:
                expanded_targets.add(dependent_target)
                queue.append(dependent_target)
    return sorted(expanded_targets)


def compute_release_manifest(
    repo_root: Path | str,
    changed_paths: Iterable[str],
    version: str,
    pr_number: int | None,
    comparison: ReleaseComparison,
) -> ReleaseManifest:
    repo_root = find_repo_root(repo_root)
    config = load_release_target_rules(repo_root)
    rules = config.projects
    normalized_changed_paths = sorted({_normalize_repo_path(path) for path in changed_paths if _normalize_repo_path(path)})

    if any(_matches_any_prefix(path, config.force_all_if_changed) for path in normalized_changed_paths):
        direct_targets = sorted(rules)
    else:
        direct_targets = sorted(
            target
            for target, rule in rules.items()
            if any(_matches_any_prefix(path, rule.paths) for path in normalized_changed_paths)
        )
    expanded_targets = _expand_targets(direct_targets, rules) if direct_targets else []

    return ReleaseManifest(
        version=version,
        pr_number=pr_number,
        comparison=comparison,
        changed_paths=tuple(normalized_changed_paths),
        direct_targets=tuple(direct_targets),
        targets=tuple(expanded_targets),
    )


def compute_release_manifest_from_git(
    repo_root: Path | str = ".",
    ref: str = "HEAD",
    pr_number: int | None = None,
) -> ReleaseManifest:
    repo_root = find_repo_root(repo_root)
    return compute_release_manifest(
        repo_root,
        changed_paths=changed_paths_since_last_version_change(repo_root, ref=ref),
        version=_read_version(repo_root, ref=ref),
        pr_number=pr_number,
        comparison=release_comparison(repo_root, ref=ref),
    )


def render_release_manifest_for_stdout(manifest: ReleaseManifest) -> str:
    return json.dumps(manifest.to_dict(), indent=2, sort_keys=True)


def render_release_manifest_from_git(
    repo_root: Path | str = ".",
    ref: str = "HEAD",
    pr_number: int | None = None,
) -> str:
    return render_release_manifest_for_stdout(
        compute_release_manifest_from_git(
            repo_root,
            ref=ref,
            pr_number=pr_number,
        )
    )


def read_release_manifest(manifest_path: Path | str) -> ReleaseManifest:
    manifest_path = Path(manifest_path)
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise click.ClickException(f"Release manifest file not found: {manifest_path}") from exc
    except json.JSONDecodeError as exc:
        raise click.ClickException(f"Invalid JSON in release manifest {manifest_path}: {exc}") from exc
    return ReleaseManifest.from_dict(data)


def resolve_publish_targets(
    repo_root: Path | str = ".",
    release_tag: str | None = None,
    release_body: str | None = None,
    release_manifest_path: Path | str | None = None,
) -> dict[str, bool]:
    manifest = (
        read_release_manifest(release_manifest_path)
        if release_manifest_path is not None
        else compute_release_manifest_from_git(repo_root)
    )
    if release_tag and manifest.version != release_tag:
        raise click.ClickException(
            f"Computed release version {manifest.version!r} does not match release tag {release_tag!r}"
        )
    targets = set(manifest.targets)

    return {
        f"publish_{target}": target in targets
        for target in sorted(PUBLISH_TARGETS)
    }
