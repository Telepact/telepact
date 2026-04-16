---
name: resolve-merge-conflicts
description: Resolve git merge conflicts safely by fetching enough history and any missing remote branches before attempting to inspect or fix the conflict.
---

# Resolve merge conflicts

Use this skill when the user asks to resolve merge conflicts, complete a merge, finish a rebase, or clean up conflict markers.

## Before resolving anything

1. Identify the branches involved and inspect the current repository state with git status.
2. Make sure the repository has enough history to inspect the conflict correctly.
3. If the repository is shallow, first run `git fetch --unshallow origin`.
4. Fetch the target branch explicitly, for example `git fetch origin main`.
5. If `git fetch --unshallow origin` fails because of a transient network issue, retry up to 3 times before giving up.

Do not try to resolve merge conflicts from a shallow repository or without fetching the branch you need to compare against.

## While resolving conflicts

- Preserve any active merge state. If `MERGE_HEAD` exists, resolve the conflicts and commit before running commands that would clear merge state.
- Inspect both sides of the conflict before editing.
- Remove conflict markers only after deciding which content to keep or how to combine both sides.
- Keep the changes focused on the conflict and any directly related fixes.

## After resolving conflicts

- Re-run the relevant existing builds, tests, or linters for the files you changed.
- Confirm `git status` no longer shows unmerged paths.
- Summarize what was resolved and note any follow-up risk or validation still needed.
