package io.github.msgpact.internal.types;

public class VFieldDeclaration {
    public final String fieldName;
    public final VTypeDeclaration typeDeclaration;
    public final boolean optional;

    public VFieldDeclaration(
            String fieldName,
            VTypeDeclaration typeDeclaration,
            boolean optional) {
        this.fieldName = fieldName;
        this.typeDeclaration = typeDeclaration;
        this.optional = optional;
    }
}
