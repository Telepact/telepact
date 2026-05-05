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

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import click
import yaml

RELEASE_CONFIG_RELATIVE_PATH = Path(".release/release-targets.yaml")
VERSION_FILE_RELATIVE_PATH = Path("VERSION.txt")
DOC_VERSIONS_RELATIVE_PATH = Path("doc/04-operate/03-versions.md")
VERSION_BUMP_MANAGED_PATHS = (
    VERSION_FILE_RELATIVE_PATH.as_posix(),
    "bind/dart/package-lock.json",
    "bind/dart/package.json",
    "bind/dart/pubspec.lock",
    "bind/dart/pubspec.yaml",
    DOC_VERSIONS_RELATIVE_PATH.as_posix(),
    "lib/java/pom.xml",
    "lib/py/pyproject.toml",
    "lib/py/uv.lock",
    "lib/ts/package-lock.json",
    "lib/ts/package.json",
    "sdk/cli/pyproject.toml",
    "sdk/cli/uv.lock",
    "sdk/console/package-lock.json",
    "sdk/console/package.json",
    "sdk/prettier/package-lock.json",
    "sdk/prettier/package.json",
)

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
    pr_number: int | None
    changed_paths: tuple[str, ...]
    direct_targets: tuple[str, ...]
    targets: tuple[str, ...]

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "pr_number": self.pr_number,
            "changed_paths": list(self.changed_paths),
            "direct_targets": list(self.direct_targets),
            "targets": list(self.targets),
        }


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


def _version_change_diff_base(repo_root: Path, ref: str = "HEAD") -> str | None:
    commits = _version_change_commits(repo_root, ref)
    if not commits:
        raise click.ClickException(f"No commits found that changed {VERSION_FILE_RELATIVE_PATH}.")
    if len(commits) < 2:
        return None
    return commits[1]


def changed_paths_since_last_version_change(repo_root: Path | str = ".", ref: str = "HEAD") -> list[str]:
    repo_root = find_repo_root(repo_root)
    base_commit = _version_change_diff_base(repo_root, ref)

    try:
        if base_commit is None:
            stdout = _git_stdout(repo_root, "ls-tree", "-r", "--name-only", ref)
        else:
            stdout = _git_stdout(repo_root, "diff", "--name-only", f"{base_commit}..{ref}")
    except subprocess.CalledProcessError as exc:
        raise click.ClickException(f"Unable to compute changed paths for release planning at {ref}: {exc.stderr.strip()}")

    changed_paths = sorted(
        {
            normalized
            for path in stdout.splitlines()
            for normalized in [_normalize_repo_path(path)]
            if normalized and normalized not in VERSION_BUMP_MANAGED_PATHS
        }
    )
    return changed_paths


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
    )


def resolve_publish_targets(
    repo_root: Path | str = ".",
    release_tag: str | None = None,
    release_body: str | None = None,
) -> dict[str, bool]:
    manifest = compute_release_manifest_from_git(repo_root)
    if release_tag and manifest.version != release_tag:
        raise click.ClickException(
            f"Computed release version {manifest.version!r} does not match release tag {release_tag!r}"
        )
    targets = set(manifest.targets)

    return {
        f"publish_{target}": target in targets
        for target in sorted(PUBLISH_TARGETS)
    }
