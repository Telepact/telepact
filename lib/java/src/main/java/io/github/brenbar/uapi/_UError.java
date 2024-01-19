package io.github.brenbar.uapi;

class _UError {
    public final String name;
    public final _UUnion errors;

    public _UError(String name, _UUnion errors) {
        this.name = name;
        this.errors = errors;
    }
}