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

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import click
import yaml

RELEASE_CONFIG_RELATIVE_PATH = Path(".release/release-targets.yaml")
RELEASE_MANIFEST_RELATIVE_PATH = Path(".release/release-manifest.json")
VERSION_FILE_RELATIVE_PATH = Path("VERSION.txt")
BUMP_VERSION_SUBJECT_PREFIX = "Bump version to "


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
class ReleaseManifest:
    version: str
    targets: tuple[str, ...]
    included_commits: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "targets": list(self.targets),
            "included_commits": list(self.included_commits),
        }


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


def release_manifest_path(repo_root: Path | str = ".") -> Path:
    return find_repo_root(repo_root) / RELEASE_MANIFEST_RELATIVE_PATH


def _normalize_repo_path(path: str) -> str:
    normalized = path.strip().strip("/")
    return normalized.replace("\\", "/")


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


def _git_log_subjects(repo_root: Path, revision: str = "HEAD") -> list[tuple[str, str]]:
    result = subprocess.run(
        ["git", "log", "--format=%H%x1f%s", revision],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True,
    )
    commits: list[tuple[str, str]] = []
    for line in result.stdout.splitlines():
        if not line:
            continue
        sha, _, subject = line.partition("\x1f")
        commits.append((sha.strip(), subject.strip()))
    return commits


def changed_paths_for_revision(repo_root: Path | str, revision: str = "HEAD") -> list[str]:
    repo_root = find_repo_root(repo_root)
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=format:", revision],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True,
    )
    return sorted(
        {
            normalized
            for path in result.stdout.splitlines()
            if (normalized := _normalize_repo_path(path))
        }
    )


def release_commits_since_last_bump(repo_root: Path | str, head_ref: str = "HEAD") -> list[ReleaseCommit]:
    repo_root = find_repo_root(repo_root)
    commits_since_last_bump: list[ReleaseCommit] = []
    for sha, subject in _git_log_subjects(repo_root, head_ref):
        if VERSION_FILE_RELATIVE_PATH.as_posix() in changed_paths_for_revision(repo_root, sha):
            break
        commits_since_last_bump.append(ReleaseCommit(sha=sha, subject=subject))
    commits_since_last_bump.reverse()
    return commits_since_last_bump


def changed_paths_for_commits(repo_root: Path | str, commits: Iterable[ReleaseCommit]) -> list[str]:
    repo_root = find_repo_root(repo_root)
    changed_paths: set[str] = set()
    for commit in commits:
        result = subprocess.run(
            ["git", "show", "--name-only", "--pretty=format:", commit.sha],
            cwd=repo_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        changed_paths.update(
            _normalize_repo_path(path)
            for path in result.stdout.splitlines()
            if _normalize_repo_path(path)
        )
    return sorted(changed_paths)


def compute_release_manifest(
    repo_root: Path | str,
    changed_paths: Iterable[str],
    version: str,
    included_commits: Iterable[ReleaseCommit] = (),
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
        targets=tuple(expanded_targets),
        included_commits=tuple(commit.subject for commit in included_commits),
    )


def write_release_manifest(repo_root: Path | str, manifest: ReleaseManifest) -> Path:
    repo_root = find_repo_root(repo_root)
    manifest_path = repo_root / RELEASE_MANIFEST_RELATIVE_PATH
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest_path


def load_release_manifest(repo_root: Path | str = ".") -> dict:
    manifest_path = release_manifest_path(repo_root)
    if not manifest_path.exists():
        raise click.ClickException(f"Release manifest not found: {manifest_path}")
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise click.ClickException(f"Invalid JSON in {manifest_path}: {exc}")
    if not isinstance(data, dict):
        raise click.ClickException(f"Release manifest must be a JSON object: {manifest_path}")
    return data


def load_release_manifest_at_commit(repo_root: Path | str, sha: str) -> dict | None:
    repo_root = find_repo_root(repo_root)
    git_path = RELEASE_MANIFEST_RELATIVE_PATH.as_posix()
    result = subprocess.run(
        ["git", "show", f"{sha}:{git_path}"],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode != 0:
        if "exists on disk, but not in" in result.stderr or "path '" in result.stderr:
            return None
        raise click.ClickException(f"git show failed for {git_path} at {sha}: {result.stderr.strip()}")

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise click.ClickException(
            f"Invalid JSON in {git_path} at {sha}: {exc}"
        )
    if not isinstance(data, dict):
        raise click.ClickException(f"Release manifest at {sha} must be a JSON object.")
    return data


def parse_legacy_release_info(subject: str, body: str) -> tuple[str, list[str]] | None:
    if not subject.startswith(BUMP_VERSION_SUBJECT_PREFIX):
        return None

    version = subject[len(BUMP_VERSION_SUBJECT_PREFIX):].split()[0]
    lines = [line.strip() for line in body.splitlines()]
    try:
        header_index = lines.index("Release targets:")
    except ValueError:
        return version, []

    targets: list[str] = []
    for line in lines[header_index + 1 :]:
        if not line:
            break
        targets.append(line)
    return version, targets


def resolve_publish_targets(
    repo_root: Path | str = ".",
    release_tag: str | None = None,
) -> dict[str, bool]:
    manifest_path = release_manifest_path(repo_root)
    if not manifest_path.exists():
        raise click.ClickException(f"Release manifest not found: {manifest_path}")

    data = load_release_manifest(repo_root)
    version = data.get("version")
    if release_tag and version != release_tag:
        raise click.ClickException(
            f"Release manifest version {version!r} does not match release tag {release_tag!r}"
        )
    targets = set(data.get("targets", []))

    return {
        f"publish_{target}": target in targets
        for target in sorted(PUBLISH_TARGETS)
    }
