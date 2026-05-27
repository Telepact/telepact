# Telepact

Telepact is an API ecosystem for all synchronous inter-process communication. It intends to make it as easy as possible to set up client-server semantics across any inter-process communication boundary.

## Motiviation

The state of software automated QA is not great. The utility of CI tests depends on the stability of the interfaces it interacts with, and our most stable interfaces that sit at the IPC boundaries have too many design concessions. Each modern major industry API technology, whether that is REST, gRPRC, or GraphQL, over-indexes on a particular goal that compromises other important categories that erode trust at the interface and therefore trust in any automated tests built on those interfaces. Trust is our stable IPC interfaces is so bad due to aesthetics/ergonomics/predictability that many devs are actively avoiding them and building tests on inherently unstable implementation interfaces all because it feels better in the short term. This hurts automated QA in the long term, because you cannot trust a test built on an unstable interface that can easily be thrown away in the future on a whim.

Telepact is an ambitious attempt to unseat the industry's most common API technologies so that automated QA actually starts to work, where devs finally feel comfortable binding tests to stable IPC interfaces. Telepact aims to usher in a world where automated tests finally sit at the stable interfaces where they are most likely to survive software evolution so that they are still there, relevant and credible at the time when a bug needs to be caught.

## Values

Telepact most values the interface description and toolchain-free ergonimics. When the interface can be accurately described in a portable manner, that unlocks trust that extends across the developer ecosystem. When the toolchain-free experience (i.e. JSON) is first-class, API accessibilty is maximized. All of the major players compromise either one or both of these values.

gRPC over-indexes on binary, which devs pay for with a burden-some code-generation heavy toolchains, and the JSON-proxy offering lacks the ergonomics of a first-class citizen design.

REST over-indexes on tradition, which devs pay for by being forced to work with type-unsafe everything-is-a-string url abstractions, and the json-schema attempt does not reign-in the wild-west of patterns and poor type-safety.

GraphQL over-indexes on client-ergonomics, which devs pay for with unpredictable server-side performance and security implications, and there is no toolchain-free out of the everything-is-a-string type-unsafe experience.

Telepact starts with a reliable interface description schema, complete with rich but non-redundant typing abstractions, and adds features from there. Because Telepact focuses first on API schema credibility and portability, things like schema-powered mocks are possible. With a strong foundation, opt-in features are added without compromising the base JSON-first API experience.

## Guidelines

Keep all of the core runtimes in `lib/` as tight implementation mirrors of one another. They all support the same Telepact spec, and should have predictable implementation that have the same file/folder patterns.

Keep Telepact runtime testing in `test/`, not in `lib/`. All of the runtimes must be held to the same standard to prevent behavior drift, so a single test harness that is applied equally to each runtime language implementation best ensures this consistency.
