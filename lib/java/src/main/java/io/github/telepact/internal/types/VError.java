package io.github.telepact.internal.types;

public class VError {
    public final String name;
    public final VUnion errors;

    public VError(String name, VUnion errors) {
        this.name = name;
        this.errors = errors;
    }
}
