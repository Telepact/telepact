package io.github.brenbar.uapi.internal;

public class UError {
    public final String name;
    public final UUnion errors;

    public UError(String name, UUnion errors) {
        this.name = name;
        this.errors = errors;
    }
}
