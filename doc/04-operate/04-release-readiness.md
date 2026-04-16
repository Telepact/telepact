# Telepact 1.0 Release Readiness

This page turns the current repository workflows into a concrete go / no-go gate
for a Telepact 1.0 release. It is intentionally scoped to what this repository
already builds, tests, documents, and publishes today.

Use it on the exact commit that would become the 1.0 release.

## 1. Explicit 1.0 exit criteria

Do not ship Telepact 1.0 unless every item below is true.

### Scope and versioning

- the 1.0 release commit has an explicit release scope, with the intended
  publish targets captured by the existing release flow (`.release/release-manifest.json`
  or the equivalent generated release metadata)
- `VERSION.txt` is set to the intended 1.0 version
- `make version` completes without leaving uncommitted changes
- the release commit is clean after version generation, which confirms the
  checked-in project versions and `doc/04-operate/03-versions.md` are aligned
  with the repository's versioning workflow

### Build, test, and packaging

- the release commit passes the existing repo-wide validation path, either by:
  - a green `Build` workflow on that commit, or
  - a successful local `make local-ci`
- every publish target included in the 1.0 release scope builds successfully in
  its current workflow path:
  - `lib/java`
  - `lib/py`
  - `lib/ts`
  - `lib/go`
  - `sdk/cli`
  - `bind/dart`
  - `sdk/console`
  - `sdk/prettier`
- the existing integration suite passes for the release commit (`make test`)
- runnable examples pass (`make example-check`)

### Contract and operations readiness

- any schema changes intended for 1.0 have a reviewed compatibility result from
  `telepact compare`, and any incompatibility is deliberate and called out as
  part of the 1.0 release decision
- the production guidance still matches the shipped runtime behavior for:
  - deployment topology
  - compatibility policy
  - auth placement
  - observability expectations
  - rollout guidance
- there is no known blocker in the documented release path:
  - release creation from `VERSION.txt` changes
  - release target resolution
  - publish workflows for the selected targets

## 2. Required docs, examples, and tooling conditions before release

These are the minimum repository conditions to treat Telepact as 1.0-ready.

### Documentation

- `README.md` still points readers to the docs landing page as the primary
  entry point
- `doc/index.md` links to the current learning, tooling, production, and
  versions pages
- the docs set includes:
  - a quickstart (`doc/example.md`)
  - tooling guidance for `fetch`, `compare`, `mock`, and `codegen`
  - production guidance for rollout, compatibility, auth, and observability
  - published version visibility in `doc/04-operate/03-versions.md`
- documentation validation passes for the edited docs:
  - `uv run --project tool/telepact_project_cli telepact-project consolidated-readme README.md /tmp/telepact-readme.md`
  - `make site`

### Examples

- every example linked from `doc/demos.md`, `doc/example.md`, or the production
  guide exists in the repository and still runs through `make example-check`
- examples cover the repo's documented production-relevant patterns that 1.0
  depends on today, especially:
  - binary negotiation
  - HTTP auth header/session propagation
  - links
  - select
  - WebSocket request/reply

### Tooling

- the CLI still provides the documented commands used by the docs and release
  workflow: `fetch`, `compare`, `mock`, and `codegen`
- the project CLI still supports the repo maintenance and release flow used in
  CI, especially:
  - `doc-versions`
  - `consolidated-readme`
  - release target resolution / release creation
- the release target map in `.release/release-targets.yaml` still matches the
  set of projects that 1.0 claims to release

## 3. Recommended validation gates

Run these gates in order on the exact release candidate commit.

1. **Version alignment gate**
   - `make version`
   - confirm `git status --short` is empty afterward
2. **Documentation gate**
   - `uv run --project tool/telepact_project_cli telepact-project consolidated-readme README.md /tmp/telepact-readme.md`
   - `make site`
3. **Examples gate**
   - `make example-check`
4. **Core integration gate**
   - `make test`
5. **Release-candidate gate**
   - `make local-ci`
6. **Schema compatibility gate**
   - run `telepact compare` for any schema changed since the last released
     baseline
   - if the result is incompatible, record the reason and make the 1.0 decision
     explicit instead of implicit

Treat any failed gate as a no-go until either:

- the issue is fixed and the gate is rerun successfully, or
- the team records a deliberate release exception with a named owner and an
  explicit reason that is acceptable for the 1.0 decision

## 4. Concise reassessment checklist

Reuse this checklist after improvements are made.

- [ ] Is the 1.0 release scope explicit and reflected in the current release metadata?
- [ ] Does `make version` leave the repo clean?
- [ ] Do docs validation and site build succeed?
- [ ] Do all linked runnable examples still pass?
- [ ] Do `make test` and `make local-ci` pass on the release candidate commit?
- [ ] Were any schema changes checked with `telepact compare` and reviewed?
- [ ] Do the current docs still cover quickstart, tooling workflow, production guidance, and published versions?
- [ ] Is there any known blocker in the release or publish workflows for the selected targets?

If any answer is "no", the default decision is **no-go for 1.0**.
