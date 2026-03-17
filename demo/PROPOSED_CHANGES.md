# Proposed Changes For Broader Telepact Adoption

This document turns the demo findings in [ASSESSMENT.md](/Users/brendanbartels/workspace/telepact/demo/ASSESSMENT.md) into a concrete repo-wide change list.

The goal is not to make Telepact “nicer”. The goal is to make it credible for broader default use by product teams, not just internal platform pilots.

## Readiness Bar

Telepact should qualify for broader use when all of the following are true:

- the same schema and same public package versions work across TypeScript, Python, and Java without transport-specific workarounds
- common nullable and optional-field flows work in every published client library
- `.telepact.yaml` authoring behaves close enough to normal YAML that new users do not hit hidden parser traps
- multi-file schema organization is explicitly supported and tested, or explicitly disallowed with strong tooling and docs
- error reporting is good enough that users can diagnose failures without patching library internals or adding temporary logging
- public documentation and examples are sufficient to build a real polyglot application using only released packages

## Priority Order

## P0: Must Fix Before Broader Rollout

### 1. Fix TypeScript null serialization

Why:

- This was the most serious functional blocker in the demo.
- It directly undermines the claim that Telepact cleanly supports null versus undefined.
- It forces application workarounds at exactly the layer that should feel easiest to adopt.

Repo changes:

- `lib/ts`
  - fix outbound request serialization when a schema allows nullable fields
  - add explicit regression tests for nullable scalars in request structs
  - add regression tests for nullable fields nested in arrays, maps, and structs
- `test/runner`
  - add cross-language cases where TypeScript sends nullable request fields to Python and Java services
  - add mirror cases where TypeScript receives nullable fields from other languages
- `doc/`
  - document the intended null/undefined semantics precisely

Acceptance criteria:

- no demo-layer workaround is required for `dueDate: null`
- TypeScript client can send schema-valid `null` values anywhere nullable types are allowed
- conformance tests pass against Python and Java servers from published packages

### 2. Define and fix multi-file schema behavior

Why:

- Real APIs quickly outgrow single-file contracts.
- The current multi-file authoring experience is not intuitive enough for broad use.
- Broader adoption needs predictable schema composition rules.

Repo changes:

- `lib/{ts,py,java}`
  - make multi-file schema loading behavior consistent across languages
  - either support top-level concatenation cleanly or fail with a precise, documented rule
- `sdk/cli`
  - add a schema validation command or improve existing validation output for multi-file composition errors
- `doc/`
  - publish the composition model with concrete examples

Acceptance criteria:

- a user can split one schema across multiple files without path-collision surprises
- if a split is invalid, the error explains exactly why and how to fix it

### 3. Make Telepact YAML behave like a deliberately documented language subset

Why:

- “Human-editable” only helps if the format is unsurprising.
- The current YAML parser is stricter than expected in ways that are hard to guess.

Repo changes:

- `lib/{ts,py,java}`
  - either support ordinary YAML flow collections or explicitly reject them with better diagnostics
- `sdk/prettier`
  - format schema files into the recommended supported subset automatically
- `sdk/cli`
  - surface actionable parse errors that mention unsupported YAML constructs by name
- `doc/`
  - publish a short “supported YAML subset” reference
  - show side-by-side examples of supported and unsupported syntax

Acceptance criteria:

- users do not have to discover parser limits through trial and error
- the formatter and docs steer schemas toward the supported subset

### 4. Improve runtime error diagnostics

Why:

- `ErrorUnknown_` is too opaque for normal debugging.
- Broad use requires strong first-party diagnostics, especially across languages.

Repo changes:

- `lib/{ts,py,java}`
  - surface the underlying cause in development-oriented logs
  - include clearer validation and serialization failure context
  - distinguish handler exceptions from request-validation failures from serializer failures
- `sdk/cli`
  - add better debug output for mock/control failures
- `doc/`
  - document common error classes and how to debug them

Acceptance criteria:

- users can tell whether a failure is caused by schema validation, serialization, transport, or handler logic
- common failures do not require patching application code just to expose the root cause

### 5. Align cross-language library ergonomics

Why:

- Broader use means mixed-language teams.
- The conceptual model is shared, but naming and usage differences still add friction.

Repo changes:

- `lib/{ts,py,java}`
  - standardize method names and option names where practical
  - if names must remain language-idiomatic, publish a clear equivalence table
  - make core concepts map one-to-one: client options, server options, message accessors, schema loading helpers
- `doc/`
  - publish a concise cross-language API comparison page

Acceptance criteria:

- the same conceptual task has recognizably similar docs and APIs in each language
- users do not need to reverse-engineer naming mismatches from source or package internals

## P1: Required To Scale Adoption Beyond Early Adopters

### 6. Publish official end-to-end examples that use only released artifacts

Why:

- Broader adoption depends on copyable examples.
- A polished public example reduces the support burden more than another conceptual document.

Repo changes:

- add an `examples/` area or equivalent public reference apps
- include at least:
  - a browser + BFF + two-service polyglot example
  - a downstream-mocked consumer test example
  - a raw JSON client example without generated code

Acceptance criteria:

- a new user can build a non-trivial app without referencing repo internals
- examples are versioned against released packages and checked in CI

### 7. Expand and centralize public docs

Why:

- The current public material is enough for exploration, not enough for a broad rollout.

Repo changes:

- `doc/`
  - add a “build your first service” guide per supported language
  - add a “raw Telepact JSON over HTTP” guide
  - add a “mocking and verification” guide with real command examples
  - add a “response shaping with `@select_`” guide
  - add a “schema organization” guide for single-file versus multi-file usage
  - add a “release/version compatibility” guide

Acceptance criteria:

- the docs cover the main adoption paths without requiring repo archaeology

### 8. Strengthen conformance and release validation across published packages

Why:

- Broader use depends on the published packages being mutually trustworthy, not just the monorepo source.

Repo changes:

- `test/runner`
  - add more published-artifact integration cases, especially for:
    - null and optional semantics
    - headers and response shaping
    - mock control APIs
    - error unions
- release tooling
  - gate package publication on cross-language conformance against the actual built artifacts

Acceptance criteria:

- package releases are backed by artifact-level integration tests, not only source-level tests

### 9. Improve code generation story or narrow the public claim

Why:

- The motivation summary claims type-safe generated code.
- Broader use requires either a mature codegen path or tighter wording.

Repo changes:

- if codegen is strategic:
  - publish official codegen guides and examples
  - add compatibility promises and generated artifact tests
- if codegen is not ready:
  - narrow the current public positioning until it is

Acceptance criteria:

- the public claim matches the actual maturity of the codegen experience

### 10. Improve versioning discipline and package coordination

Why:

- Broader adoption needs predictable package coordination across ecosystems.
- Even when versions match numerically, users need confidence that npm, PyPI, Maven, and CLI releases are compatible.

Repo changes:

- release tooling
  - publish synchronized version notes
  - document compatibility expectations between runtimes and CLI
- `doc/versions.md` or equivalent
  - make version compatibility easy to find and understand

Acceptance criteria:

- users know which package versions are intended to work together

## P2: Important For Long-Term Default Use

### 11. Add first-party development helpers

Why:

- Broad use improves when the ecosystem reduces repeated bootstrapping work.

Repo changes:

- `sdk/cli`
  - consider commands for schema validation, formatting, and local smoke-testing
  - improve `fetch` and `mock` discovery/documentation
- templates or examples
  - add starter templates per language

### 12. Expand message/header examples beyond internal features

Why:

- The motivation claim around metadata is stronger if normal business metadata is demonstrated, not only internal headers like `@select_`.

Repo changes:

- `doc/`
  - add examples of request/response headers for auth, tracing, and pagination-like metadata
- `test/runner`
  - add conformance cases for custom headers

### 13. Decide whether to broaden or narrow current product messaging

Why:

- Some motivation claims are supported strongly today.
- Some are directionally correct but ahead of current implementation polish.

Repo changes:

- `doc/motivation.md`
  - keep the strengths that were clearly demonstrated:
    - polyglot portability
    - debuggable JSON wire format
    - built-in mocking
    - response shaping
  - soften or qualify claims whose current package behavior is not yet broad-rollout ready:
    - accessibility
    - null/undefined ergonomics in practice
    - frictionless human-editable schema authoring

Acceptance criteria:

- the positioning matches what released packages can do reliably today

## Concrete Repo Areas To Change

These are the highest-impact areas in the broader repo:

- `lib/ts`
  - null handling
  - serializer diagnostics
  - API ergonomics
- `lib/py`
  - diagnostics parity
  - ergonomics parity
- `lib/java`
  - diagnostics parity
  - ergonomics parity
- `sdk/cli`
  - validation output
  - schema authoring feedback
  - mock UX
- `sdk/prettier`
  - supported YAML style normalization
- `doc/`
  - YAML subset
  - multi-file composition
  - debugging
  - version compatibility
  - official guides
- `test/runner`
  - artifact-level cross-language conformance
  - nullable-field cases
  - header cases
  - mock-control cases
- public examples/templates
  - released-package-only demo apps

## Suggested Sequencing

### Phase 1

- fix TypeScript null serialization
- improve diagnostics
- lock down multi-file schema behavior
- document YAML subset

### Phase 2

- publish official released-artifact examples
- improve docs and version compatibility guidance
- expand conformance coverage

### Phase 3

- align cross-language ergonomics
- mature codegen or narrow that claim
- tighten product positioning to match actual maturity

## Final Recommendation

If the repo wants Telepact to qualify for broader use, the path is clear:

1. fix the real functional blockers
2. remove authoring surprises
3. improve diagnostics
4. publish first-class public examples and docs
5. back the whole thing with artifact-level cross-language conformance

The protocol already has enough substance to justify this investment. The broader repo now needs to turn that substance into a product experience that feels dependable to teams who are not willing to reverse-engineer alpha behavior.
