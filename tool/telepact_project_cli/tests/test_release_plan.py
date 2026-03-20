import json
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_ROOT))

from telepact_project_cli.commands.doc_versions import _latest_released_versions
from telepact_project_cli.release_plan import (
    compute_release_manifest,
    load_release_manifest,
    write_release_manifest,
)


class ReleasePlanTests(unittest.TestCase):
    def test_compute_release_manifest_uses_declarative_rules_and_dependency_expansion(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            (repo_root / "VERSION.txt").write_text("1.0.0-alpha.214", encoding="utf-8")
            (repo_root / ".release").mkdir()
            (repo_root / ".release" / "release-targets.yaml").write_text(
                textwrap.dedent(
                    """
                    projects:
                      py:
                        paths: [lib/py]
                        expands_to: [cli]
                      ts:
                        paths: [lib/ts]
                        expands_to: [dart, console]
                      cli:
                        paths: [sdk/cli]
                      console:
                        paths: [sdk/console]
                      dart:
                        paths: [bind/dart]
                      prettier:
                        paths: [sdk/prettier]
                        expands_to: [console]
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )

            manifest = compute_release_manifest(
                repo_root,
                changed_paths=[
                    "lib/ts/src/main.ts",
                    "sdk/prettier/package.json",
                    "README.md",
                ],
                version="1.0.0-alpha.215",
                pr_number=300,
            )
            manifest_path = write_release_manifest(repo_root, manifest)
            loaded = load_release_manifest(repo_root)

            self.assertEqual(manifest.direct_targets, ("prettier", "ts"))
            self.assertEqual(loaded["targets"], ["console", "dart", "prettier", "ts"])
            self.assertEqual(loaded["changed_paths"], [
                "README.md",
                "lib/ts/src/main.ts",
                "sdk/prettier/package.json",
            ])
            self.assertEqual(manifest_path.resolve(), (repo_root / ".release" / "release-manifest.json").resolve())

    def test_latest_released_versions_prefers_manifest_history_and_falls_back_to_legacy_commits(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            subprocess.run(["git", "init"], cwd=repo_root, check=True, capture_output=True, text=True)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_root, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo_root, check=True)

            (repo_root / "VERSION.txt").write_text("1.0.0-alpha.200", encoding="utf-8")
            subprocess.run(["git", "add", "VERSION.txt"], cwd=repo_root, check=True)
            subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_root, check=True)

            subprocess.run(
                [
                    "git",
                    "commit",
                    "--allow-empty",
                    "-m",
                    "Bump version to 1.0.0-alpha.201 (#1)\n\nRelease targets:\njava",
                ],
                cwd=repo_root,
                check=True,
            )

            (repo_root / ".release").mkdir()
            (repo_root / ".release" / "release-manifest.json").write_text(
                json.dumps(
                    {
                        "version": "1.0.0-alpha.202",
                        "pr_number": 2,
                        "changed_paths": ["lib/py/pyproject.toml"],
                        "direct_targets": ["py"],
                        "targets": ["cli", "py"],
                    },
                    indent=2,
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )
            subprocess.run(["git", "add", ".release/release-manifest.json"], cwd=repo_root, check=True)
            subprocess.run(
                ["git", "commit", "-m", "Bump version to 1.0.0-alpha.202 (#2)"],
                cwd=repo_root,
                check=True,
            )

            versions = _latest_released_versions(repo_root, ["java", "py", "cli"])

            self.assertEqual(
                versions,
                {
                    "py": "1.0.0-alpha.202",
                    "cli": "1.0.0-alpha.202",
                    "java": "1.0.0-alpha.201",
                },
            )


if __name__ == "__main__":
    unittest.main()
