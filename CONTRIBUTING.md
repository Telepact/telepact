# Contributing

Thanks for your interest in contributing to the Telepact project!

## Folder Structure

The Telepact project is structed as a monorepo.

-   `common` - files commonly used across the Telepact ecosystem
-   `bind` - contains lightweight wrapper libraries that use bindings to expose
    a formal Telepact implementation in a language not yet targetted by a formal
    Telepact implementation.
-   `lib` - contains all formal library implementations of Telepact in various
    programming languages
-   `test` - contains the test framework that enforces the Telepact
    specification on all implementations found in `lib`
-   `sdk` - contains various programs that assist developing in the Telepact
    ecosystem
-   `tool` - contains various programs that assist the development of the
    Telepact project

## Building and Testing

There are several top-level `Makefile` commands for building and testing the
various subprojects.

Example:

```
make java
make test-java
make clean-java
```

Most of these commands simply delegate to a `Makefile` in the related
subproject. In some cases, it may be simpler to change your working directory to
the related subproject for greater control over the build tools in that
subproject.
