package io.github.brenbar.japi;

public class UFieldDeclaration {
    public final String fieldName;
    public final UTypeDeclaration typeDeclaration;
    public final boolean optional;

    public UFieldDeclaration(
            String fieldName,
            UTypeDeclaration typeDeclaration,
            boolean optional) {
        this.fieldName = fieldName;
        this.typeDeclaration = typeDeclaration;
        this.optional = optional;
    }
}
