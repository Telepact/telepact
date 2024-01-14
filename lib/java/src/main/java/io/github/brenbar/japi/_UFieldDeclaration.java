package io.github.brenbar.japi;

public class _UFieldDeclaration {
    public final String fieldName;
    public final _UTypeDeclaration typeDeclaration;
    public final boolean optional;

    public _UFieldDeclaration(
            String fieldName,
            _UTypeDeclaration typeDeclaration,
            boolean optional) {
        this.fieldName = fieldName;
        this.typeDeclaration = typeDeclaration;
        this.optional = optional;
    }
}
