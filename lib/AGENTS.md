# Library Agent Instructions

These instructions apply to the language libraries under `lib/`, including:

- `lib/go`
- `lib/java`
- `lib/py`
- `lib/ts`

## One Logical Implementation

Treat the language libraries as parallel implementations of the same Telepact core, not as independent projects.

When changing one library, assume the equivalent change likely belongs in the others unless there is a concrete, language-specific reason it does not.

## Layout Mirroring

The library projects should continue to use pseudo-identical layouts.

That means:

- The same major subsystems should exist in each library.
- The same responsibilities should live in corresponding directories and files.
- Exact naming and casing may follow language conventions.
- Exact packaging roots may follow language conventions.
- "Same file spirit" matters more than byte-for-byte naming.

Examples:

- If one library has a schema parsing subsystem, the others should have the same subsystem.
- If one library splits schema loading, validation, coordinate lookup, and parse-failure mapping into separate files, the others should do the same in spirit.
- If one library adds a new internal helper or subsystem for protocol behavior, the others should gain the corresponding helper or subsystem unless there is a documented reason not to.

## Semantic Consistency

Do not let the libraries drift apart in implementation semantics.

In particular, keep these behaviors aligned across languages:

- schema parsing and validation
- wire format behavior
- request/response processing
- error mapping and failure shapes
- source coordinate behavior used by tests
- deterministic helper behavior where cross-language parity matters

If a behavior must differ by language, treat that as an exception to justify and document, not as the default.

## Refactors

When restructuring one library:

- look for the corresponding files in the other libraries
- preserve the same conceptual boundaries across languages
- avoid introducing an abstraction in one library that causes the others to become structurally incomparable

Small idiomatic differences are fine. Structural drift is not.

## New Features And Fixes

When adding a feature or fixing a bug in one library:

- check whether the same change is needed in the other libraries
- update tests that enforce cross-language behavior
- keep naming, failure semantics, and directory placement aligned in spirit

Do not treat a change as complete if it leaves the libraries semantically out of sync.

## Allowed Differences

These differences are acceptable when required by the language ecosystem:

- package manager and build tool layout
- language-idiomatic file naming and casing
- source root conventions
- minimal glue needed for runtime, typing, or distribution

These differences are not a reason to diverge in core Telepact behavior or subsystem organization.
