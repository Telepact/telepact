package uapi.internal.types;

public class UError {
    public final String name;
    public final UUnion errors;

    public UError(String name, UUnion errors) {
        this.name = name;
        this.errors = errors;
    }
}
